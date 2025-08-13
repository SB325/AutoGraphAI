from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from rdflib import Graph, Namespace
import os, sys

from dotenv import load_dotenv
load_dotenv('.env')   

neo4j_uri = os.getenv("NEO4J_URI")
db_name = os.getenv("GRAPH_DB")
user = os.getenv("USERN")
passwd = os.getenv("PASSWD")

auth_data = {'uri': neo4j_uri,
             'database': db_name,
             'user': user,
             'pwd': passwd}

# Define your prefixes
prefixes = {
    'neo4ind': Namespace('http://neo4j.org/ind#'),
    'neo4voc': Namespace('http://neo4j.org/vocab/sw#'),
    'nsmntx': Namespace('http://neo4j.org/vocab/NSMNTX#'),
    'apoc': Namespace('http://neo4j.org/vocab/APOC#'),
    'graphql': Namespace('http://neo4j.org/vocab/GraphQL#')
}
# Define your custom mappings & store config
config = Neo4jStoreConfig(auth_data=auth_data,
                          custom_prefixes=prefixes,
                          handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.IGNORE,
                          batching=True)

file_path = './ontologies/CommonCoreOntologiesMerged.ttl'

# Create the RDF Graph, parse & ingest the data to Neo4j, and close the store(If the field batching is set to True in the Neo4jStoreConfig, remember to close the store to prevent the loss of any uncommitted records.)
neo4j_aura = Graph(store=Neo4jStore(config=config))
# Calling the parse method will implictly open the store
neo4j_aura.parse(file_path, format="ttl")
neo4j_aura.close(True)