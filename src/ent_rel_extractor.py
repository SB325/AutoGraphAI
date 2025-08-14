from neo4j_graphrag.experimental.components.entity_relation_extractor import (
    LLMEntityRelationExtractor,
)
from neo4j_graphrag.llm import OpenAILLM
import asyncio
import pdb

extractor = LLMEntityRelationExtractor(
            llm=OpenAILLM(
                model_name=self.model_name,
                model_params={
                    "max_tokens": 1000,
                    "response_format": {"type": "json_object"},
                },
            )
        )

class entityRelationshipExtractor():
    def __init__(self):
        self.model_name = 'llama3:8b'
        self.max_tokens = 1000

    async def extract_facts(self, text_to_extract: str):
        await extractor.run(chunks=TextChunks(chunks=[TextChunk(text="some text")]))
    
    async def show_entities_relationships(self):
        return extractor.nodes, extractor.edges