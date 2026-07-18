import json
import spacy
from dotenv import load_dotenv
from entities_to_ui import display_text_annotations
import pdb
import os
import copy
import argparse

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

def token_pos(doc, verbose: bool = True):
    tokens = []
    for token in doc:
        if (token.pos_ != 'NOUN') & (token.pos_ != 'PRON') & (token.pos_ != 'CARDINAL'):
            continue
        # print(f"Text: {token.text}")
        # print(f"Position: {token.idx}")
        # print(f"Coarse POS Tag (pos_): {token.pos_}")    # Universal POS tag
        # print(f"Fine-grained Tag (tag_): {token.tag_}")  # Detailed Penn Treebank tag
        # print(f"Explanation: {spacy.explain(token.tag_)}")
        tokens.append(token)
    return tokens
    # Determine if it's a noun and classify its category
    # NOUN = Common Noun, PROPN = Proper Noun
    # is_noun = ent.label_ in ["NOUN", "PROPN"]
    
    # if is_noun:
    #     noun_category = "PROPER_NOUN" if ent.label_ == "PROPN" else "COMMON_NOUN"
    # else:
    #     noun_category = "NOT_A_NOUN"
        
    # Structure the token dictionary exactly as requested

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
        trailing_character = ''
        if ')' in text[ent.start_char + len(ent.text) ]:
            trailing_character = ')'

        ent_data = {
            "token_string": ent.text + trailing_character,
            "first_character_index": ent.start_char,
            "token_length": len(ent.text + trailing_character),
            "token_type": {
                "pos": ent.label_,  # e.g., 'PROPN', 'VERB', 'DET', 'PUNCT'
                # "is_noun": is_noun,
                # "noun_category": noun_category
            }
        }
        ent_list.append(ent_data)
    tokens = token_pos(doc, verbose) 

    token_list = []
    for tok in tokens:
        if tok.idx in [ind['first_character_index'] for ind in ent_list]:
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

def decontiguize_entities(sample_text: str, entity_list: dict, verbose: bool):
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

    # text_sample = """
    #     The Foreign Ministry communicated the complaints to the US 
    #     ambassador before filing them in the United States. 
        
    #     He was very receptive to 
    #     our concerns regarding alleged human rights violations against Mexicans in 
    #     detention centers, as well as the deaths of three Mexicans during operations 
    #     by ICE (Immigration and Customs Enforcement),” she said. 
        
    #     The president emphasized that protecting Mexicans abroad must be a national cause, 
    #     amidst an escalation of her government’s actions regarding the situation 
    #     of immigrants in the US. 
        
    #     Days earlier, following the death of Salgado Araujo 
    #     during an operation, Sheinbaum had indicated that the response would go 
    #     “beyond” diplomatic notes.
    #     """

    output = analyze_tokens(text_sample, verbose=False)
    
    sorted_output = sorted(output, key=lambda x: x["first_character_index"])

    # Function that combines entities that are contiguous (not separated by another
    # word or punctuation mark.)
    clean_sorted_output = decontiguize_entities(text_sample, sorted_output, verbose)

    text_list = []
    for out in clean_sorted_output:
        val = {"start": out['first_character_index'], 'length': out['token_length']}
        text_list.append(val)

    payload = {
        'text': text_sample,
        'ranges': text_list,
    }
    
    display_text_annotations(payload)