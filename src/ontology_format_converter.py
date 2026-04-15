import os
from rdflib import Graph
from typing import Sequence
import pdb

def extension_test(filename: str, expected_ext: str | Sequence[str]) -> bool:
    ext = os.path.splitext(filename)[1].lower()

    allowed = [expected_ext.lower()] \
        if isinstance(expected_ext, str) else \
        [e.lower() for e in expected_ext]

    if ext in allowed:
        print(f"Extension is valid {ext}")
        return True
    else:
        print(f"Wrong extension: {ext} was provided instead of {expected_ext}.")
        return False

# 1. Initialize the Graph
g = Graph()

def rdf_xml_to_ttl(inputfile: str, outputfile: str, verbose: bool):
    try:
        if verbose:
            print(f"Parsing {inputfile} to {outputfile}")
        if not extension_test(inputfile, ['.rdf','.xml']):
            print(f"Inputfile is not \'.rdf\' or \'.xml\'.")
        else:
            g.parse(inputfile, format="xml")
            if verbose:
                print(f"Parsed {inputfile} to {outputfile}")

            if verbose:
                print(f"Serializing {inputfile} to {outputfile}")
            if extension_test(outputfile, '.ttl'):
                g.serialize(destination=outputfile, format="turtle")
            else:
                print(f"Outputfile is not '.ttl'.")
            if verbose:
                print(f"Written to {outputfile}")

    except Exception as e:
        print(f"Error parsing and serializing  {inputfile} to {outputfile}:\n{e}")

def ttl_to_rdf_xml(inputfile: str, outputfile: str, verbose: bool):
    try:
        if verbose:
            print(f"Parsing {inputfile} to {outputfile}")
        if not extension_test(inputfile, '.ttl'):
            print(f"Inputfile is not '.ttl'.")
        else:
            g.parse(inputfile, format="turtle")
            if verbose:
                print(f"Parsed {inputfile} to {outputfile}")

            if verbose:
                print(f"Serializing {inputfile} to {outputfile}")
            if extension_test(outputfile, ['.rdf','.xml']):
                g.serialize(destination=outputfile, format="xml")
            else:
                print(f"Outputfile is not \'.rdf\' or \'.xml\'.")
            if verbose:
                print(f"Written to {outputfile}")

    except Exception as e:
        print(f"Error parsing and serializing  {inputfile} to {outputfile}:\n{e}")

def ttl_to_jsonld(inputfile: str, outputfile: str, verbose: bool):
    try:
        if verbose:
            print(f"Parsing {inputfile} to {outputfile}")
        if not extension_test(inputfile, '.ttl'):
            print(f"Inputfile is not '.ttl'.")
        else:
            g.parse(inputfile, format="turtle")
            if verbose:
                print(f"Parsed {inputfile} to {outputfile}")

            if verbose:
                print(f"Serializing {inputfile} to {outputfile}")
            jsonld_data = g.serialize(format="json-ld")

            if extension_test(outputfile, '.jsonld'):
                with open(outputfile, "w") as f:
                    f.write(jsonld_data)
            else:
                print(f"Outputfile is not '.jsonld'.")
            if verbose:
                print(f"Written to {outputfile}")
    except Exception as e:
        print(f"Error parsing and serializing  {inputfile} to {outputfile}:\n{e}")

def rdf_xml_to_jsonld(inputfile: str, outputfile: str, verbose: bool):
    try:
        if verbose:
            print(f"Parsing {inputfile} to {outputfile}")
        if not extension_test(inputfile, ['.rdf','.xml']):
            print(f"Inputfile is not \'.rdf\' or \'.xml\'.")
        else:
            g.parse(inputfile, format="xml")
            if verbose:
                print(f"Parsed {inputfile} to {outputfile}")

            if verbose:
                print(f"Serializing {inputfile} to {outputfile}")
            jsonld_data = g.serialize(format="json-ld")

            if extension_test(outputfile, '.jsonld'):
                with open(outputfile, "w") as f:
                    f.write(jsonld_data)
            else:
                print(f"Outputfile is not '.jsonld'.")
            if verbose:
                print(f"Written to {outputfile}")
    except Exception as e:
        print(f"Error parsing and serializing  {inputfile} to {outputfile}:\n{e}")