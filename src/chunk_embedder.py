from neo4j_graphrag.experimental.components.embedder import TextChunkEmbedder
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
import asyncio

class embedder():
    def __init__(self):
        self.embedder = TextChunkEmbedder(embedder=OpenAIEmbeddings())

    async def embed(self, text_to_embed: str):
        await self.embedder.run(
            text_chunks=TextChunks(
                chunks=[TextChunk(text="my_text")]
                )
            )
        return self.embedder.result

