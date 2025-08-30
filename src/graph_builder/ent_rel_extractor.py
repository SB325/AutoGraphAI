from neo4j_graphrag.experimental.components.entity_relation_extractor import (
    LLMEntityRelationExtractor,
)
from neo4j_graphrag.experimental.components.types import TextChunks, TextChunk
from neo4j_graphrag.generation.prompts import PromptTemplate, ERExtractionTemplate

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

triplet_extraction_prompt = '''For the following chunks of text, extract the subject, 
        predicate and object tokens. 

        For each subject, predicate and object, return a label. For example, 
        if the subject is someone named Jack, return "PERSON" as the label. 
        If the predicate is "worked at the mall", the label can be "IS EMPLOYED AT". If the 
        object is a ACME Inc., return "COMPANY" as the object label. That was only an example. 
        Use exact tokens from the text when extracting the predicate instead of paraphrasing. 

        The response must be in json format with two keys in the base object: 
        "nodes" and "relationships". The nodes object value holds a list of subject 
        and object information, while the relationships value holds a list of predicate 
        information.

        The values of the nodes key should be a list of json objects containing 
        the key "id" that holds a number string denoting the order of the subject or object entities,
        The key "label" that holds the category of the subject or object entities, 
        and the key "properties" that contains a json object describing the subject or object entities.
        The properties object contains a set of key value pairs. The key "matched_name" whose value is the 
        exact string representation of the entity taken directly from the text. The key "official_name" 
        which is the official name of the subject, and a "description" key containing a string that holds 
        a semantic description of the subject or object that is at least 8 tokens long. 
        
        The values for the relationships key should be a list of json objects containing 
        the keys "type", "start_node_id", "end_node_id" and "properties".
        The value for "type" is a string representing the name of the relationship and
        can be the exact string representing the predicate as taken from the text.
        The value for "start_node_id" is the id value of the subject node.
        The value for "end_node_id" is the id value of the object node.
        The value for "properties" is a json object containing a key named "description".
        The value of the description key is a string representing the semantic meaning of the 
        predicate/relationship.

        Here is an example: 
        {{
            "nodes": [ 
                {{"id": "0", "label": "Person", "properties": 
                    {{
                        "matched_name": "Sultan of Swat", 
                        "official_name": "Babe Ruth", 
                        "description": "person named John"
                    }}
                }}, 
                {{"id": "1", "label": "Person", "properties":
                    {{
                        "matched_name": "R. Nixon", 
                        "official_name": "Richard Nixon", 
                        "description": "Former president of the United States",
                    }}
                }}
            ], 
            "relationships": [
                {{"label": "KNOWS", "start_node_id": "0", "end_node_id": "1", "properties":
                    {{"description": "is familliar with"}}
                }}
            ]
        }}

        Do not preface the response with any other text. Only return a json string.

        Chunk: {text} \
        Answer: 
        '''

class entityRelationshipExtractor():
    def __init__(self):
        self.extractor = LLMEntityRelationExtractor(
            llm=OllamaLLM(
                model_name=model_name,
                model_params={
                    "max_tokens": 1000,
                    "response_format": {"type": "json_object"},
                    "options": {"host": 'http://172.18.0.11:11434'},
                },
            ),
            prompt_template=PromptTemplate(
                template=triplet_extraction_prompt,
                expected_inputs=['text'],
            ),
        )

    async def extract_facts(self, chunk_block):
        return await self.extractor.run(
            schema=None,
            chunks=TextChunks(chunks=chunk_block),
            document_info = None,
            lexical_graph_config = None,
        )


if __name__ == "__main__":
    ## The Entity-Relationship Extractor takes embedded chunks
    #  extract_facts results in pydantic validation error that I havent' 
    # solved yet.

    # Load Data
    with open('text_samples/trump_putin.txt', 'r') as file_object:
        sample = file_object.read().replace("\n","").replace("\'s","s")
    print("Loaded Data...")

    # Chunk text sample
    chunks = asyncio.run(
        text_splitter(
            input_text=sample,
            chunk_size=400,
            )
        )
    print("Chunked Text...")

    # Embed chunks
    emb=embedder()
    embeddings = emb.embed(chunks.chunks)
    print("Embedded Chunks...")

    # Extract ontological facts (Entities, Relationships)
    facts=entityRelationshipExtractor()

    # pdb.set_trace()
    start = time()

    triples = asyncio.run(facts.extract_facts(embeddings[:3]))
    print(f"Triple construction time: {(time()-start)/60} minutes")

    [print(f"{node.label} | {node.properties['text']} | {node.id}") if 'text' in node.properties.keys() else print(f"{node.label} | {node.properties['matched_name']} | {node.properties['official_name']} | {node.properties['description']} | {node.id}") for node in triples.nodes ]
    [print(f"{rel.start_node_id} | {rel.type} | {rel.end_node_id}") for rel in triples.relationships]
    pdb.set_trace()


    ''''
    Relationship list:
    [print(f"{rel.start_node_id} | {rel.type} | {rel.end_node_id}") for rel in triples.relationships]
    Entity List:
    [print(f"{node.label} | {node.properties['text']} | {node.id}") if 'text' in node.properties.keys() else print(f"{node.label} | {node.properties['matched_name']} | {node.properties['official_name']} | {node.properties['description']} | {node.id}") for node in triple
s.nodes ]

    Reification Example:
    https://www.w3.org/TR/rdf12-concepts/#section-triple-terms-reification
    Chunk | Recognition from the worlds most powerful country, America, that Western efforts to isolate the Kremlin leader have failed | 377294ed-5c22-4187-8c39-8bbcb79c19a7
    RDF triple #1 Subject: "Western Efforts", Object: "Kremlin Leader", Predicate: "failed to isolate"
    Reifying RDF triple: Subject: "America", Predicate: "Recognition that" -> triple #1

    Chunk | The fact that this high-level meeting is happening is testament to that, as is the joint press conference that the Kremlin has announced | 60f116cc-a226-49be-a684-eb166e164a33
    Triple: Subject: "high-level meeting", Object: "the Kremlin", Predicate: "Testimony to"
    True Object is "that", referring to previous chunk. Suggesting that chunk size is too small in this case.

    ---- KG Development Strategies ----
    The triple elements need not be lexical matches with tokens in text, often makes sense that they are multi-token descriptions of specific concepts
    Chunk size of 400 tokens performs better than 200 tokens.
    Node descriptions can be used to help flag potential errors in node labels.
    Node descriptions along with node labels can be used for entity resolution.
    Node matched_name can be used to identify the entity within the chunk. 
    Node official_name can be used to represent the official name of the entity, which sometimes is not the same as the 
    matched_name ({"matched_name": "Putin", "official_name": "Vladimir Putin"}).
    Entity resolved nodes (as the same entity) will merge on "official_name" property.
    Relationship type can be long and elaborate. The llm can summarize to a more generalizable form.

    ---- Post KG Generation ----
    Schema can be easily derived from the cleaned KG. 
    (
    Without building the KG first, it is impossible/impractical to create a schema unless the domain is well known, fixed and rigid.
    When you want to build a KG, let the LLM do the heavy lifting, work with it to refine, then the schema generation is trivial.
    )

    ---- Notes ----
    1) Prompt development
        - describe the task: for each chunk derive the subject, predicate and objects. 
        - describe the output format in detail (For json, describe the keys at each level and the form and meaning that the values should have.)
        - give an example.
        - remind the model to exclude anything other than the output data structure (json).
    2) Configure the LLMEntityRelationshipExtractor
        - ensure prompt and json output can fit in the context window of max_tokens length.
        - state output type (json)
        - split documents into chunks of size around 400 tokens.
    3) Run and debug the extractor over entire document
    4) Use interractive processing to correct/clean/dedupe node/relationship elements
        - Compare node descriptions to node labels to help identify errors in node labels (cosine distance of embedded descriptions and labels)
        - Perform entity resolution using node descriptions, labels and names as attributes.
        - Summarize relationships with long verbose types to get a more canonical/generalizable representation.
    5) Use KG to derive schema
        - Trivial step
    6) Analyze schema to find and correct illogical relationship patterns
        - Corrections should propagate to constituent graphs.
    7) Use Minimap document display to review quality of node/relationship extraction
        - Identify gaps in extraction
        - Identify potentially reified triplets
        - Identify extraction errors from context
        7b) Use minimap review to make additional improvements to the KG
            - Can manually select entities, in conjunction with existing ones and re-run LLM on relevant chunks.
            - Update schema
        
    Additional potential steps:
    Asyncronous/parallel extraction + manual interraction for multiple documents.

    ---- Document types (unstructured text) ----
    News reports
    SEC filings
    '''
