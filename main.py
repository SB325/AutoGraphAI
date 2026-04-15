
import argparse
from src.ontology_format_converter import (
    rdf_xml_to_ttl, 
    ttl_to_rdf_xml, 
    ttl_to_jsonld, 
    rdf_xml_to_jsonld,
)

def convert(input_file, output_file, verbose: bool = False) -> bool:
    input_ext = os.path.splitext(input_file)[1].lower():
    output_ext = os.path.splitext(output_file)[1].lower():

    if 'jsonld' in input_ext:
        print('Conversions from jsonld to rdf, ttl not available.')
        return False

    if input_ext in ['xml', 'rdf']:
        if 'ttl' in output_ext: 
            rdf_xml_to_ttl(input_file, input_file)
        if 'jsonld' in output_ext:
            ttl_to_jsonld(input_file, input_file)
    if input_ext in 'ttl':
        if output_ext in ['xml', 'rdf']: 
            ttl_to_rdf_xml(input_file, input_file)
        if 'jsonld' in output_ext:
            ttl_to_jsonld(input_file, input_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Ontology Format Converter',
        description='This script converts ontologies between RDF/XML, TTL and JSONLD formats.',
        epilog='Example: python onto-convert.py ' \
            + 'ontologies/financial/GLEIF/RDF_FILES/ontology.xml' \ 
            + 'ontologies/financial/GLEIF/RDF_FILES/ontology.jsonld --verbose',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-i", "--input_file",   help="Source ontology path.")
    parser.add_argument("-o", "--output_file",  help="Destination ontology path.")
    parser.add_argument("-v", "--verbose",      help="Verbose output.")

