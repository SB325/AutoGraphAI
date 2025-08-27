from neo4j_graphrag.experimental.components.schema import SchemaFromTextExtractor
from neo4j_graphrag.experimental.components.types import TextChunks, TextChunk
from neo4j_graphrag.generation.prompts import PromptTemplate
from neo4j_graphrag.llm import OllamaLLM
from text_splitter import text_splitter
import os
import pdb
from dotenv import load_dotenv
from chunk_embedder import embedder
from time import time
from json_repair import repair_json

load_dotenv() 
model_name = os.getenv("EMBEDDING_MODEL_NAME")
import asyncio


triplet_extraction_prompt = '''For the following chunks of text, extract the subject, 
        predicate and object tokens. 

        For each subject, predicate and object, return a label (category). For example, 
        if the subject is someone named Jack, return "PERSON" as the category. 
        If the predicate is "worked at the mall", return "IS EMPLOYED AT". If the 
        object is a ACME Inc., return "COMPANY" as the object. That was only an example. 
        Use exact tokens from the chunk when extracting the predicate instead of paraphrasing. 

        The response must be in json format with three keys in the base object: 
        "node_types", "relationship_types" and "patterns". The node_types 
        object value holds the subject and object information, the relationship_types value holds the predicate 
        information and the patterns value holds the labels of the subject, object and predicate as a 
        list of lists. 

        The values of the node_types key should be a nested json object containing 
        the key "id" that holds a number string denoting the order of the subject, predicate or object,
        The key "label" that holds the category of the subject, object or predicate, 
        and the key "properties" that contains a list of objects.
        The "properties" objects contain the keys "name", "type" and "description".
        The value for "name" is the exact match of the subject, object or predicate of the category.
        The value for "type" is the string representation of the category and can be one of the following
        values:

        "BOOLEAN",
        "DATE",
        "DURATION",
        "FLOAT",
        "INTEGER",
        "LIST",
        "LOCAL_DATETIME",
        "LOCAL_TIME",
        "POINT",
        "STRING",
        "ZONED_DATETIME",
        "ZONED_TIME"

        The value for "key" is a text description of the category. 

        The values of the relationship_types key should be a nested json object containing 
        a "label" key, a "start_node_id" key, an "end_node_id" key and a "properties" key. 
        The "label" value is a single token representation of the relationship between 
        the subject and object. 
        The "start_node_id" and "end_node_id" values are the values of the "id" fields
        from the respective subject or object node_type object values.
        The properties value has the same structure as in the node_types object. 

        Here is an example: 
        {{
            "node_types": [ 
            {{"id": "0", "label": "Person", "properties": [
                {{"name": "John", "type": "STRING", "description": ""}}
            ] }}, 
            {{"id": "1", "label": "Person", "properties": [
                {{"name": "Jane", "type": "STRING", "description": ""}} 
            ]
            }}
            ], 
            "relationship_types": [
                {{"label": "KNOWS", "start_node_id": "0", "end_node_id": "1", "properties":[
                    {{"name": FAMILIAR", "type": "STRING", "description": ""}}
                ] }}
            ], 
            "patterns": [['Person', 'KNOWS', 'Person' ]]
        }}

        Do not preface the response with any other text. Only return a json string.

        Chunk: {text} \
        Answer: 
        '''

class auto_schema_builder():
    def __init__(self):
        # Instantiate the automatic schema extractor component
        self.schema_extractor = SchemaFromTextExtractor(
                llm=OllamaLLM(
                model_name=model_name,
                model_params={
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"},
                },
            ),
            prompt_template=PromptTemplate(
                template=triplet_extraction_prompt,
                expected_inputs=['text'],
            ),
        )

    async def extract(self, chunk_block: str):
        # Extract the schema from the text
        # pdb.set_trace()
        return await self.schema_extractor.run(
                    text=chunk_block[0].text) #TextChunks(chunks=chunk_block))
                    # examples=example)

if __name__ == "__main__":

    # Load Data
    with open('text_samples/trump_putin.txt', 'r') as file_object:
        sample = file_object.read().replace("\n","").replace("\'s","s")
    print("Loaded Data...")

    # Chunk text sample
    chunks = asyncio.run(text_splitter(input_text=sample, chunk_size=200, chunk_overlap= 0))
    print("Chunked Text...")

    # Embed chunks
    emb=embedder()
    embeddings = emb.embed(chunks.chunks)
    print("Embedded Chunks...")

    asb = auto_schema_builder()

    start = time()
    graph_schema = asyncio.run(asb.extract(embeddings[:1]))
    print(f"Triple construction time: {(time()-start)/60} minutes")
    pdb.set_trace()