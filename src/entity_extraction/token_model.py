import json
import spacy
from dotenv import load_dotenv
from entities_to_ui import display_text_annotations
import pdb
import os
import copy
import argparse
import re

load_dotenv()
spacy_model = os.getenv("SPACY_MODEL")

labels = {
    "PERSON": "People, including fictional characters.",
    "NORP": "Nationalities, or religious or political groups.",
    "FAC": "Buildings, airports, highways, bridges, and other infrastructure.",
    "ORG": "Companies, agencies, institutions, and organizations.",
    "GPE": "Geo-political entities, such as countries, cities, and states.",
    "LOC": "Non-GPE locations, mountain ranges, or bodies of water.",
    "PRODUCT": "Objects, vehicles, foods, etc. (does not include services).",
    "EVENT": "Named hurricanes, battles, wars, or sports events.",
    "WORK_OF_ART": "Titles of books, songs, movies, or academic papers.",
    "LAW": "Named documents made into laws or legal regulations.",
    "LANGUAGE": "Any named, distinct language.",
    "DATE": "Absolute or relative dates or specific calendar periods.",
    "TIME": "Times of day smaller than 24 hours.",
    "PERCENT": "Percentage values (includes \"%\" and textual values).",
    "MONEY": "Monetary values, including their specific currency units.",
    "QUANTITY": "Physical measurements, such as weight, area, or distance.",
    "ORDINAL": "Sequential numbers like “first”, “second”, or “3rd”.",
    "CARDINAL": "Numerals, digits, or amounts that do not fit into other types.",
}

def get_word_at_index(text, index):
    # Find all sequences of alphanumeric characters and their spans
    for match in re.finditer(r'\w+', text):
        start, end = match.span()
        # Check if the target index falls within this word's boundaries
        if start <= index < end:
            return match.group()
    return None

def token_pos(doc, ent_list, verbose: bool = True):
    tokens = []
    for token in doc:
        if 'which' in token.text:
            continue
        if (token.pos_ != 'NOUN') & (token.pos_ != 'PRON') & (token.pos_ != 'PROPN') & (token.pos_ != 'CARDINAL'):
            continue
        cont = False
        for ent in ent_list:
            if token.text in ent['token_string']:
                if (token.idx >= ent['first_character_index']) & \
                    (token.idx < (ent['first_character_index'] + ent['token_length'])):
                    # This token is within an lready established entity label. continue
                    cont=True
                    break
        if cont:
            continue
        if verbose:
            print(f"Text: {token.text}")
            print(f"Position: {token.idx}")
            print(f"Coarse POS Tag (pos_): {token.pos_}")    # Universal POS tag
            print(f"Fine-grained Tag (tag_): {token.tag_}")  # Detailed Penn Treebank tag
            print(f"Explanation: {spacy.explain(token.tag_)}")
        tokens.append(token)
    return tokens

def analyze_tokens(text: str, verbose: bool = True) -> list:
    """Tokenizes a string and returns metadata about each token."""
    # Load the English NLP model
    try:
        nlp = spacy.load(spacy_model)
    except OSError:
        raise OSError("Please install the spaCy model using: python -m spacy download en_core_web_sm")
    
    # Process the text
    doc = nlp(text)
    ent_list = []

    for ent in doc.ents:
        # Edge case: closed parenthesis missing
        token = ent.text
        trailing_character = ''
        start_char = ent.start_char

        if '[' in ent.text:
            continue
        # if '(' in ent.text:
        #     continue
        # if ')' in ent.text:
        #     pdb.set_trace()
        #     continue
        ent_data = {
            "token_string": token + trailing_character,
            "first_character_index": start_char,
            "token_length": len(token + trailing_character),
            "token_type": {
                "pos": ent.label_,  # e.g., 'PROPN', 'VERB', 'DET', 'PUNCT'
            }
        }
        ent_list.append(ent_data)
    tokens = token_pos(doc, ent_list, verbose) 

    token_list = []
    for tok in tokens:
        if tok.idx in [ind['first_character_index'] for ind in ent_list]:
            continue
        if tok.idx in [ind['token_string'] for ind in ent_list]:
            continue
        token_list.append(
            {
                "token_string": tok.text,
                "first_character_index": tok.idx,
                "token_length": len(tok.text),
                "token_type": {
                    "pos": tok.pos_,
                }
            }
        )

    ent_list.extend(token_list)

    return ent_list

def tag_all_instances(text_sample: str, clean_sorted_output: list, indices: list):
    # find all indices ( [val[2] for val in indices ] ) 
    #   that are not in 
    #   [ val["first_character_index"] for val in clean_sorted_output ]
    #  and tag them.

    # first char index of all recorded inds matching ent

    recorded_inds = [ val["first_character_index"] for val in clean_sorted_output if 
        (val['token_string'] in indices[0][0]) | (indices[0][0] in val['token_string']) ]
    recorded_tokens = [ val["token_string"] for val in clean_sorted_output if 
        (val['token_string'] in indices[0][0]) | (indices[0][0] in val['token_string']) ]
    
    # If all indices matching ent are recorded already, spacy got them all, nothing to add
    if len(recorded_inds) == len(indices):
        return 

    # pos of all ents matching inds
    pos = [ val["token_type"]["pos"] for val in clean_sorted_output if indices[0][0] in val['token_string'] ]

    untagged_inds = []
    for ind in indices:
        if ind[1] not in recorded_inds:
            # is this ind a matching ent or a substring of a word/token
            # if single word:
            if not ind[0].count(" "):
                # omit erroneous non-nouns from clean_sorted_output list
                if 'the' in get_word_at_index(text_sample, ind[1]):
                    continue
                if get_word_at_index(text_sample, ind[1]) not in recorded_tokens[0]:
                    continue
            # if multi-word token:
            else:
                if ind[0] != recorded_tokens[0]:
                    continue
            untagged_inds.append(
                {
                    "token_string": ind[0],
                    "first_character_index": ind[1],
                    "token_length": len(ind[0]),
                    "token_type": {
                        "pos": pos[0],
                    }
                }
            )
    clean_sorted_output.extend(untagged_inds)

def decontiguize_entities(sample_text: str, entity_list: list, verbose: bool):
    decontiguized_entities = []
    skip = False
    for ind, ent in enumerate(entity_list[:-1]):
        
        # slice gap_text from entity character ends
        gap_text = sample_text[
            (ent['first_character_index'] + ent['token_length']) :
            entity_list[ind+1]['first_character_index']
        ]
        
        if skip:
            # This contiguous (second) entity was absorbed into first, so skip 
            skip = False
            continue

        copied_ent = copy.deepcopy(ent)
        decontiguized_entities.append(copied_ent)

        gap_text_ = "".join(gap_text.split())
        if (',' not in gap_text_) & \
            ('.' not in gap_text_) & \
            (len(gap_text_)==0):

            # Edge case: multi token long entity is on newline
            if '\n' in gap_text:
                gap_text = gap_text.replace('\n', ' ')

            decontiguized_entities[-1]["token_string"] = \
                copied_ent['token_string'] + gap_text + entity_list[ind+1]['token_string']
            decontiguized_entities[-1]["first_character_index"] = copied_ent['first_character_index']
            decontiguized_entities[-1]["token_length"] = \
                copied_ent['token_length'] + \
                entity_list[ind+1]['token_length'] + \
                len(gap_text)
            if verbose:
                print(f"{decontiguized_entities[-1]['token_string']}")
            skip = True

    copied_ent = copy.deepcopy(entity_list[-1])
    decontiguized_entities.append(copied_ent)
    return decontiguized_entities

# --- Example Usage ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text_sample", required=True, help="Sample Text for Entity extraction.")
    parser.add_argument("-v", "--verbose", action='store_true', help="Print label outputs.", default=False)

    args = parser.parse_args()

    text_sample_file = args.text_sample
    verbose = args.verbose

    with open(text_sample_file, "r", encoding="utf-8") as file:
        text_sample = file.read()
        if verbose:
            print(text_sample)

    output = analyze_tokens(text_sample, verbose=False)
    
    sorted_output = sorted(output, key=lambda x: x["first_character_index"])

    # Function that combines entities that are contiguous (not separated by another
    # word or punctuation mark.)
    clean_sorted_output = decontiguize_entities(text_sample, sorted_output, verbose)
    

    for ent in clean_sorted_output:
        try:
            indices = [(m.group(), m.start()) for m in re.finditer(rf"{ent['token_string']}(?=[\s\W])", text_sample)]
        except:
            pass
        if len(indices) > 1:
            # Find untagged instances of tagged entities in text and tag them
            tag_all_instances(text_sample, clean_sorted_output, indices)

    text_list = []
    for out in clean_sorted_output:
        val = {"start": out['first_character_index'], 'length': out['token_length']}
        text_list.append(val)

    payload = {
        'text': text_sample,
        'ranges': text_list,
    }

    # pdb.set_trace()
    display_text_annotations(payload)