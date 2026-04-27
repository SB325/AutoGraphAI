import os
import re

def find_ontology_base_urls(directory):
    # Regex: starts with http://, matches non-whitespace characters, ends with .org
    # [^\s]*? makes it non-greedy to avoid capturing multiple URLs in one line
    pattern = re.compile(r'(https?://[^\s"<>]*?)/">')
    found_urls = {}

    # Recursively walk through the directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.rdf', '.xml')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Find all unique matches in this file
                        matches = set(pattern.findall(content))
                        if matches:
                            found_urls[file_path] = sorted(list(matches))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    
    return found_urls