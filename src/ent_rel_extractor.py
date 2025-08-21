from neo4j_graphrag.experimental.components.entity_relation_extractor import (
    LLMEntityRelationExtractor,
)
from neo4j_graphrag.experimental.components.types import TextChunks, TextChunk
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

class entityRelationshipExtractor():
    def __init__(self):
        self.extractor = LLMEntityRelationExtractor(
            llm=OllamaLLM(
                model_name=model_name,
                model_params={
                    "max_tokens": 1000,
                    "response_format": {"type": "json_object"},
                },
            )
        )

    async def extract_facts(self, chunk_block):
        return await self.extractor.run(chunks=TextChunks(chunks=chunk_block))
    
    async def show_entities_relationships(self):
        return self.extractor.nodes, self.extractor.edges

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
    triples = asyncio.run(facts.extract_facts(embeddings[:2]))
    print(f"Triple construction time: {(time()-start)/60} minutes")
    pdb.set_trace()