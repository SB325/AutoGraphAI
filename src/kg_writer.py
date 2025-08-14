import neo4j
from neo4j_graphrag.experimental.components.kg_writer import Neo4jWriter
from neo4j_graphrag.experimental.components.types import Neo4jGraph
import asyncio

from dotenv import load_dotenv
load_dotenv('.env')   
user = os.getenv("USERN")
passwd = os.getenv("PASSWD")
neo4j_uri = os.getenv("NEO4J_URI")

async def kg_writer(nodes, relationships):
    with neo4j.GraphDatabase.driver(
            url="bolt://localhost:7687", 
            auth=(user, passwd)
            ) as driver:
        writer = Neo4jWriter(driver)
        graph = Neo4jGraph(nodes=[], relationships=[])
        await writer.run(graph)
    
    print(f"{len(nodes)} nodes and {len(relationships)} written to neo4j.\n")

# Adjust the batch_size parameter of Neo4jWriter to optimize insert 
# performance. This parameter controls the number of nodes or 
# relationships inserted per batch, with a default value of 1000.