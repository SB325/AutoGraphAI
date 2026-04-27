import re
from collections import Counter
import json
import pdb
import spacy
from spacy.matcher import Matcher
from dotenv import load_dotenv
import os 

load_dotenv() 
model_name = os.getenv("SPACY_MODEL")

nlp = spacy.load(model_name)
matcher = Matcher(nlp.vocab)
# Matches optional auxiliaries/adverbs followed by a verb (e.g., "is finishing", "will submit")
pattern = [{"POS": {"IN": ["AUX", "ADV"]}, "OP": "*"}, {"POS": "VERB"}]
matcher.add("VERB_PHRASE", [pattern])

def extract_concepts(text):
    doc = nlp(text)

    concepts_data = {}
    word_counts = Counter()
    
    # Process by sentence to keep context
    for sent in doc.sents:
        # Extract Noun Chunks (multi-word concepts)

        noun_chunks = list(sent.noun_chunks)
        
        # 2. Get Verb Phrases via the pre-defined matcher
        verb_matches = matcher(sent)
        verb_spans = [sent[start:end] for _, start, end in verb_matches]
        
        # Combine and filter to avoid overlaps (e.g., if a word is in a noun chunk and a verb phrase)
        from spacy.util import filter_spans
        all_phrases = filter_spans(noun_chunks + verb_spans)

        for span in all_phrases:
            # Clean token: remove stops and lower case
            clean_token = " ".join([t.text.lower() for t in span if not t.is_stop])
            
            if not clean_token.strip():
                continue

            # Determine Part of Speech
            # If it's a noun chunk, label as NOUN. If from matcher, label as VERB.
            pos_label = "VERB" if any(t.pos_ in ["VERB", "AUX"] for t in span) else "NOUN"

            word_counts[clean_token] += 1
            
            if clean_token not in concepts_data:
                concepts_data[clean_token] = {
                    "sentences": [], 
                    "positions": [],
                    "pos": pos_label
                }

            # Update data
            if sent.text not in concepts_data[clean_token]["sentences"]:
                concepts_data[clean_token]["sentences"].append(sent.text)
            
            # Position relative to start of sentence
            concepts_data[clean_token]["positions"].append(span.start_char - sent.start_char)

    return [{"token": t, **concepts_data[t]} for t, _ in word_counts.most_common()]

if __name__ == "__main__":
    # Example usage
    with open('src/text_samples/military/sample.txt', 'r', encoding='utf-8') as file:
        raw_article_text = file.read()
    
    # clean_content = " ".join(raw_article_text.split())
    data = extract_concepts(raw_article_text)

    # Display first few results
    print(json.dumps(data[:5], indent=2,  ensure_ascii=False))
    pdb.set_trace()