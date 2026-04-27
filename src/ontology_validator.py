import io, sys, os
from owlready2 import *
from rdflib import Graph
from utils.find_base_urls import find_ontology_base_urls
import pdb
from pathlib import Path
import requests
from owlready2 import locstr, declare_datatype, default_world, Restriction
import json

default_world._cached_universe = None

# Define the missing datatype with its required converters
declare_datatype(
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString", 
    str,
    str,
    lambda x: x,   
)

# 1. Define the main world and storage
# All ontologies loaded here will "see" each other
ontology_paths = (
    'ontologies/financial/FIBO/RDF_FILES/',
    # 'ontologies/financial/FBO/RDF_FILES/',
    'ontologies/financial/GLEIF/RDF_FILES/',
)

def combine_ontology_paths(ont_paths: set = ontology_paths) -> list:
    results = []
    paths = []
    # search recursively for the base urls of ontologies referenced in the RDF files.
    for opath in ont_paths:
        obj_paths = find_ontology_base_urls(opath)
        
        if isinstance(obj_paths, list):
            for obj in obj_paths:
                results.extend(obj.values()[0])
        else:
            paths.extend([ val for val in obj_paths.keys() ])
            urls = [val + '/' if not val.endswith('/') else val for vals in obj_paths.values() for val in vals]

            results.extend(urls)

    results_list = list(set(results))
    paths_list = list(set(paths))
    return paths_list

def get_uri(iri: str):
    response = requests.get(iri, allow_redirects=True)
    return response.url

def load_to_owlready(file_path, master_onto):
    """Parses RDF via RDFLib and merges it into Owlready2"""
    
    # print(f"--- Loading {file_path} ---")
    # g = Graph()
    # g.parse(file_path, format="xml")
    
    # # Export to RDF/XML (the format Owlready2 handles best)
    # rdf_data = g.serialize(format="xml")
    
    if not master_onto:
        master_onto = get_ontology(f"file://{file_path}").load()
    else:
        with master_onto:
            master_onto.load(f"file://{file_path}")

    return master_onto

def gather_ontologies(ont_paths = None):
    if ont_paths is None:
        ont_paths = ontology_paths

    paths_list = combine_ontology_paths(ont_paths)

    master_onto = None
    for path in paths_list:
        try:
            master_onto = load_to_owlready(path, master_onto)
        except Exception as e:
            print(f"Failed to merge {path}: {e}")

    # Run FBO converter for rdfs of FBO!!
    # 3. Verify the combination
    print(f"\nTotal classes in combined graph: {len(list(master_onto.classes()))}")

    # 4. Run the Reasoner to check for conflicts across ALL merged files
    """ The reasoner performs a series of Reparenting, or changing the superclass
        of an existing class. Inspect master_onto before and after reasoner to 
        better understand the ramifications.
    """
    print("\nRunning Reasoner to check for conflicts...")
    with master_onto:
        sync_reasoner(ignore_unsupported_datatypes = True)
        # sync_reasoner_pellet(infer_property_values=True)

    # 5. Check results
    conflicts = list(default_world.inconsistent_classes())
    if conflicts:
        print("!!! CONFLICTS FOUND !!!")
        print(f"The following classes are logically inconsistent: {conflicts}")
    else:
        print("SUCCESS: Combined ontology is logically consistent.")
    
    return master_onto

def get_graph(save: bool = False, filename: str = "ontology.json"):
    graph = default_world.as_rdflib_graph()

    if save:
        json_ld_string = graph.serialize(format="json-ld")

        # 3. Parse string into a Python dict/JSON object
        ontology = json.loads(json_ld_string)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(ontology, f, indent=4)
    
    return graph

def get_langstring_triples(onto):
    """Get all triples containing rdf:langString values"""
    from rdflib import Namespace
    
    # Convert Owlready2 ontology to rdflib graph
    graph = onto.as_rdflib_graph()
    
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    
    # Find all triples with language-tagged literals
    langstring_triples = []
    for subject, predicate, obj in graph:
        # Check if object is a literal with a language tag
        if hasattr(obj, 'language') and obj.language:
            langstring_triples.append((str(subject), str(predicate), str(obj), obj.language))
    
    return langstring_triples

if __name__ == "__main__":
    # Pass set of string paths to gather_ontologies() to get ontologies from special 
    #   directories
    master_ontology = gather_ontologies()
    
    graph = get_graph(True, "ontology.json")
    
    triples = master_ontology.get_triples()

    object_dict = {}
    cnt = 0
    for subj, pred, obje in triples:
        sub = None
        pre = None
        obj = None
        try:
            sub = default_world._get_by_storid(subj)
        except:
            pass

        if sub:
            try:
                pre = default_world._get_by_storid(pred)
            except:
                pass
            try:
                obj = default_world._get_by_storid(obje)
            except:
                pass
            # pdb.set_trace()
            content = {}   
            if pre:
                content.update({
                    'property': {
                        'is_a': str(pre.is_a),
                        'storid': pre.storid,
                        'name': pre.name,
                        'full_name': str(pre),
                        'iri': pre.iri,
                    }
                })
            if obj:
                content.update({
                    'object': {
                        'is_a': str(obj.is_a),
                        'storid': obj.storid,
                        'name': obj.name,
                        'full_name': str(obj),
                        'iri': obj.iri
                    }
                })

            if object_dict.get(sub.iri, None):
                if content: 
                    prop = object_dict[sub.iri].get('property', None)
                    odict = object_dict[sub.iri].get('object', None)
                    if prop:
                        if pre:
                            if not pre.storid in [tng.get('storid', None) for tng in prop]:
                                object_dict[sub.iri]['property'].append(content['property']) 
                    elif pre:
                        object_dict[sub.iri]['property'] = [content['property']]
                    if odict:
                        if obj:
                            if not obj.storid in [tng.get('storid', None) for tng in odict]:
                                object_dict[sub.iri]['object'].append(content['object']) 
                    elif obj:
                        object_dict[sub.iri]['object'] = [content['object']]
            else:
                object_dict.update({
                    sub.iri: {
                        'is_a': str(sub.is_a),
                        'storid': sub.storid,
                        'name': sub.name,
                        'full_name': str(sub),
                        'iri': sub.iri,
                    }   
                })
        cnt=cnt+1


    with open("ontology_dict.json", "w", encoding="utf-8") as f:
        json.dump(object_dict, f, indent=4)

    pdb.set_trace()