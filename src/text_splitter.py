from langchain_text_splitters import CharacterTextSplitter
from neo4j_graphrag.experimental.components.text_splitters.langchain import LangChainTextSplitterAdapter
import asyncio

async def text_splitter(input_text: str):
    splitter = LangChainTextSplitterAdapter(
        CharacterTextSplitter(chunk_size=4000, chunk_overlap=200, separator=".")
    )
    await splitter.run(text="Hello World. Life is beautiful.")
