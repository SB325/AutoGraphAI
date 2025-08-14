from neo4j_graphrag.experimental.components.neo4j_reader import Neo4jChunkReader
from neo4j_graphrag.experimental.components.types import LexicalGraphConfig, TextChunks
import asyncio

# optionally, define a LexicalGraphConfig object
# shown below with the default values

async def chunk_reaader():
    config = LexicalGraphConfig(
        chunk_node_label="Chunk",
        document_node_label="Document",
        chunk_to_document_relationship_type="PART_OF_DOCUMENT",
        next_chunk_relationship_type="NEXT_CHUNK",
        node_to_chunk_relationship_type="PART_OF_CHUNK",
        chunk_embedding_property="embeddings",
    )
    reader = Neo4jChunkReader(driver)
    result = await reader.run(lexical_graph_config=config)

    return result