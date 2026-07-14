import asyncio
import pdb
import os
from dotenv import load_dotenv
from time import time
from gliner2 import GLiNER2
import time

load_dotenv() 
model_name = os.getenv("EMBEDDING_MODEL_NAME")

class entityRelationshipExtractor():
    def __init__(self):
        # Use a multi-task version for relationship support
        self.model = GLiNER2.from_pretrained(
            model_name,
            map_location="cuda"
        )
        self.model.quantize() 
        self.model.compile()

    def extract_facts(self, 
            text: set, 
            labels: set = None, 
            thresh: int = 0.35, 
            rel_thresh: int = 0.25,
        ):

        schema = self.model.create_schema().entities(labels["entity_types"]).relations(labels["relation_types"])

        results = self.model.extract(
            text, 
            schema,
        )

        return results

if __name__ == "__main__":

    text = """Mr. Satya Nadella has served as Chief Executive Officer and a director of 
        "Microsoft Corporation since February 2014. Previously, he served as 
        "Executive Vice President of Microsoft's Cloud and Enterprise group."""

    labels = {
        "entity_types": {
            # "Executive": "",
            # "Title": "",
            "Company": "",
            "Date": "",
            "Department": "",
        },
        "relation_types": {
            "works_for": "Employment relationship where person works at organization",
            "founded": "Founding relationship where person created organization",
            # "acquired": "Acquisition relationship where company bought another company",
            "located_in": "Geographic relationship where entity is in a location"
        }
    }

    start = time.perf_counter()
    ERE = entityRelationshipExtractor()

    start_run = time.perf_counter()
    results = ERE.extract_facts(text,labels)

    end = time.perf_counter()
    
    print("SEC Extraction Results:")

    for rel in results['relation_extraction']:
        pdb.set_trace()
        head = results['entities'][rel['head']]
        tail = results['entities'][rel['tail']]
        print(f"[{head['text']}] --({rel['label']})--> [{tail['text']}]")

    print(f"Startup time: {(start_run - start):.2f} seconds.\n \
            Extraction time: {(end-start_run):.2f} seconds.\n")

    pdb.set_trace()