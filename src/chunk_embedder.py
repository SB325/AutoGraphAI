from neo4j_graphrag.experimental.components.embedder import TextChunkEmbedder
from neo4j_graphrag.embeddings.ollama import OllamaEmbeddings
import asyncio
import pdb
from dotenv import load_dotenv
from text_splitter import text_splitter
import os

load_dotenv() 
model_name = os.getenv("EMBEDDING_MODEL_NAME")

class embedder():
    def __init__(self):
        self.embedder = TextChunkEmbedder(
                    embedder=OllamaEmbeddings(
                    model = model_name,
                    ))

    def embed(self, chunks: list):
        embedded_chunks = [self.embedder._embed_chunk(text_chunk) for text_chunk in chunks]
        return embedded_chunks


if __name__ == "__main__":
    ## The Chunk Embedder embeds chunks from the `text_splitter` and returns an object containing
    # text: The text string of the chunk
    # index: The index of the list of splits
    # metadata['embedding']: vector embedding of the chunk
    emb=embedder()

    with open('text_samples/trump_putin.txt', 'r') as file_object:
        sample = file_object.read().replace("\n","").replace("\'s","s")

    chunks = asyncio.run(text_splitter(sample))
    embeddings = emb.embed(chunks.chunks)

