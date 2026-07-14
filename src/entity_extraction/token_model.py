import json
import spacy
from dotenv import load_dotenv
import pdb
import os

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
        print(f"Text: {token.text}")
        print(f"Position: {token.idx}")
        print(f"Coarse POS Tag (pos_): {token.pos_}")    # Universal POS tag
        print(f"Fine-grained Tag (tag_): {token.tag_}")  # Detailed Penn Treebank tag
        print(f"Explanation: {spacy.explain(token.tag_)}")
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
        ent_data = {
            "token_string": ent.text,
            "first_character_index": ent.start_char,
            "token_length": len(ent.text),
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

# --- Example Usage ---
if __name__ == "__main__":
    sample_text = """
        The Foreign Ministry communicated the complaints to the US 
        ambassador before filing them in the United States. 
        
        He was very receptive to 
        our concerns regarding alleged human rights violations against Mexicans in 
        detention centers, as well as the deaths of three Mexicans during operations 
        by ICE (Immigration and Customs Enforcement),” she said. 
        
        The president emphasized that protecting Mexicans abroad must be a national cause, 
        amidst an escalation of her government’s actions regarding the situation 
        of immigrants in the US. 
        
        Days earlier, following the death of Salgado Araujo 
        during an operation, Sheinbaum had indicated that the response would go 
        “beyond” diplomatic notes.
        """
    
    output = analyze_tokens(sample_text, verbose=False)
    
    sorted_output = sorted(output, key=lambda x: x["first_character_index"])

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(sorted_output, file, indent=4)
