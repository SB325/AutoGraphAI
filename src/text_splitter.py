from langchain_text_splitters import CharacterTextSplitter
from neo4j_graphrag.experimental.components.text_splitters.langchain import LangChainTextSplitterAdapter
import asyncio
import pdb
import ast

async def text_splitter(input_text: str, chunk_size: int = 200, chunk_overlap: int = 100):
    ## Splits Document into chunks of size <chunk_size> or smaller with <chunk_overlap>
    #  character overlaps between consecutive chunks. Yields an object <splits> that contains
    #  text, index (of chunk), metadata and uid for each chunk. A dictionary can be obtained 
    #  by splits.chunks[10].model_dump().
    splitter = LangChainTextSplitterAdapter(
        CharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap, 
            separator=".")
    )
    
    splits = await splitter.run(text=input_text)
    return splits

if __name__ == "__main__":
    with open('text_samples/trump_putin.txt', 'r') as file_object:
        sample = file_object.read().replace("\n","").replace("\'s","s")

    splits = asyncio.run(text_splitter(sample))
