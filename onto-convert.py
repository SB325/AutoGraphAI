
import os, sys
import argparse
from src.ontology_format_converter import (
    rdf_xml_to_ttl, 
    ttl_to_rdf_xml, 
    ttl_to_jsonld, 
    rdf_xml_to_jsonld,
)
import pdb
from pathlib import Path
from tqdm import tqdm
import shutil

def convert(input_file: str, output_file: str, verbose: bool = False) -> bool:
    success = False
    try:
        input_ext = os.path.splitext(input_file)[1].lower()
        output_ext = os.path.splitext(output_file)[1].lower()

        if '.jsonld' in input_ext:
            print('Conversions from jsonld to rdf, ttl not available.')
            return success
        if input_ext in ['.xml', '.rdf']:
            if '.ttl' in output_ext: 
                rdf_xml_to_ttl(input_file, output_file, verbose)
            if '.jsonld' in output_ext:
                rdf_xml_to_jsonld(input_file, output_file, verbose)
        if input_ext in '.ttl':
            if output_ext in ['.xml', '.rdf']: 
                ttl_to_rdf_xml(input_file, output_file, verbose)
            if '.jsonld' in output_ext:
                ttl_to_jsonld(input_file, output_file, verbose)
        success = True
    except:
        if verbose: print(f"Failed to process {input_file}")
    
    return success

def divergent_paths(input: str, output: str):
    input_path = os.path.splitext(Path(input).resolve())[0].split("/")
    output_path = os.path.splitext(Path(output).resolve())[0].split("/")

    diverged_path = '.'
    for cnt, infolder in enumerate(input_path):
        if infolder not in output_path[cnt]:
            diverged_path = input_path[cnt+1:-1]
            break

    return diverged_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Ontology Format Converter\n',
        description='This script converts ontologies between RDF/XML, TTL and JSONLD formats.',
        epilog='Example: python onto-convert.py ' \
            + 'ontologies/financial/GLEIF/RDF_FILES/ontology.xml' \
            + 'ontologies/financial/GLEIF/RDF_FILES/ontology.jsonld --verbose',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-i", "--input_file",   required=True,      help="Source ontology path.")
    parser.add_argument("-o", "--output_file",  required=True,      help="Destination ontology path.")
    parser.add_argument("-ext", "--output_ext", help="Destination ontology extension (Only, and Must be used if input is a directory).")
    parser.add_argument("-v", "--verbose",      action='store_true', help="Verbose output.")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    
    nfiles = 1
    failed_files = []
    if Path(input_file).is_dir():
        if not args.output_ext:
            print(f"###### Error! ######\nMust include --output_ext argument if input_file is a directory! Exiting.\n")
            sys.exit(0)
        
        out_ext = args.output_ext
        valid_extensions = ['.rdf', '.xml', '.ttl', '.jsonld']
        files = [ f.as_posix() for f in Path(input_file).rglob("*") if f.is_file() ] # and os.path.splitext(f)[1].lower() in valid_extensions ]
        nfiles = len(files)

        pbar = tqdm(files)
        for file in pbar:
            in_ext = os.path.splitext(file)[1].lower()
            path_and_name = os.path.splitext(file)[0]
            output_path = os.path.splitext(output_file)[0]
            
            diverged_path = '/'.join(divergent_paths(path_and_name, output_path))
            out_file_root = os.path.join(output_path, diverged_path)
            out_file_path = out_file_root + '/' + path_and_name.split("/")[-1] + out_ext
            out_file_copy_path = out_file_root + '/' + path_and_name.split("/")[-1] + in_ext

            Path(out_file_root).mkdir(parents=True, exist_ok=True)

            if in_ext in valid_extensions:
                success = convert(file, out_file_path)
            else:
                try:
                    shutil.copy2(file, out_file_copy_path)
                    success = True
                except:
                    success = False

            if success:
                pbar.set_description(f"Successfully Processed {file}")
            else:
                pbar.set_description(f"Failed to Process {file}")
                failed_files.append(file)

    elif Path(input_file).isfile():
        success = convert(input_file, output_file, args.verbose)
        if not success:
            failed_files.append(file)
    
    nsucceeded = nfiles-len(failed_files)
    nfailed = len(failed_files)
    print(f"###### Summary: ######\n {nsucceeded} of {nfiles} files successfully processed.\n")
    if nfailed:
        print(f"\nFailed Files:\n")
        [print(f"{failed_file}\n") for failed_file in failed_files]
