from neo4j_graphrag.experimental.components.entity_relation_extractor import (
    LLMEntityRelationExtractor,
)
from neo4j_graphrag.experimental.components.types import TextChunks, TextChunk
from neo4j_graphrag.generation.prompts import PromptTemplate

from neo4j_graphrag.llm import OllamaLLM
import asyncio
import pdb
import os
from dotenv import load_dotenv
from text_splitter import text_splitter
from chunk_embedder import embedder
from time import time

load_dotenv() 
model_name = os.getenv("EMBEDDING_MODEL_NAME")

# example = {{"nodes": [ {{"id": "0", "label": "Person", "properties": {{"name": "John"}} }}]' \
#         + ', "relationships": [{{"type": "KNOWS", "start_node_id": "0", "end_node_id": "1", "properties": ' \
#         + '{{"since": "2024-08-01"}} }}] }}

triplet_extraction_prompt = 'For the following chunks of text, extract the subject, predicate and object tokens. ' \
        + 'For each subject, predicate and object, return a category. For example, if the subject is someone named Jack, ' \
        + 'return "PERSON" as the category. If the predicate is "worked at the mall", return "IS EMPLOYED AT". If the ' \
        + 'object is a ACME Inc., return "COMPANY" as the object. That was only an example. Use exact tokens from the chunk ' \
        + 'when extracting the predicate instead of paraphrasing. ' \
        + 'For the response, ensure that it is in json format with two keys in the same base object: ' \
        + '"nodes" and "relationships". The nodes ' \
        + 'object value holds the subject and object information, while the relationships value holds the predicate ' \
        + 'information. The values of the nodes key should be a nested json object containing ' \
        + 'the key "id" that holds a number string denoting the order of the subject, predicate or object, the key "label" ' \
        + 'that holds the exact string of the subject, object ' \
        + 'or predicate from the prompt text, and the key "properties" that contains the the name of the category. The ' \
        + 'values of the relationships key should be a nested json object containing a properties key, a "start_node_id" ' \
        + 'key and "end_node_id" key that hold the "id" values from the subject and object nodes respectively. ' \
        + 'Here is an example: {{"nodes": [ {{"id": "0", "label": "Person", "properties": {{"name": "John"}} }}, '\
        + '{{"id": "1", "label": "Person", "properties": {{"name": "Jane"}} }}]' \
        + ', "relationships": [{{"type": "KNOWS", "start_node_id": "0", "end_node_id": "1", "properties": ' \
        + '{{"FAMILIAR"}} }}] }}. Do not preface the response with any other text. ' \
        + 'Only return a json string. Enclose the values of the nodes and relationships objects in square brackets. ' \
        + 'Chunk: {text} ' \
        + 'Answer: '

class entityRelationshipExtractor():
    def __init__(self):
        self.extractor = LLMEntityRelationExtractor(
            llm=OllamaLLM(
                model_name=model_name,
                model_params={
                    "max_tokens": 1000,
                    "response_format": {"type": "json_object"},
                },
            ),
            prompt_template=PromptTemplate(
                template=triplet_extraction_prompt,
                expected_inputs=['text'],
            ),
        )

    async def extract_facts(self, chunk_block):
        return await self.extractor.run(chunks=TextChunks(chunks=chunk_block))


if __name__ == "__main__":
    ## The Entity-Relationship Extractor takes embedded chunks
    #  extract_facts results in pydantic validation error that I havent' 
    # solved yet.

    # Load Data
    with open('text_samples/trump_putin.txt', 'r') as file_object:
        sample = file_object.read().replace("\n","").replace("\'s","s")
    print("Loaded Data...")

    # Chunk text sample
    chunks = asyncio.run(text_splitter(sample))
    print("Chunked Text...")

    # Embed chunks
    emb=embedder()
    embeddings = emb.embed(chunks.chunks)
    print("Embedded Chunks...")

    # Extract ontological facts (Entities, Relationships)
    facts=entityRelationshipExtractor()

    # pdb.set_trace()
    start = time()

    triples = asyncio.run(facts.extract_facts(embeddings[:1]))
    print(f"Triple construction time: {(time()-start)/60} minutes")
    # triples.nodes[0].nodes/relationships/patterns
    pdb.set_trace()