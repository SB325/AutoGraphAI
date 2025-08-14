from neo4j_graphrag.experimental.pipeline.components.lexical_graph_builder import LexicalGraphBuilder
from neo4j_graphrag.experimental.pipeline.components.types import LexicalGraphConfig
import asyncio

lexical_graph_builder = LexicalGraphBuilder(config=LexicalGraphConfig())

async def graph_builder(input_chunks: list): 
    graph = await lexical_graph_builder.run(
        text_chunks=TextChunks(chunks=input_chunks),
        document_info=DocumentInfo(path="my_document.pdf"),
    )

    return graph

# [
#     TextChunk(text="some text", index=0),
#     TextChunk(text="some text", index=1),
# ]