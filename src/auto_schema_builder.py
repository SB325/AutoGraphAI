from neo4j_graphrag.experimental.components.schema import SchemaFromTextExtractor
from neo4j_graphrag.llm import OpenAILLM

# Instantiate the automatic schema extractor component
schema_extractor = SchemaFromTextExtractor(
    llm=OpenAILLM(
        model_name="gpt-4o",
        model_params={
            "max_tokens": 2000,
            "response_format": {"type": "json_object"},
        },
    )
)

# Extract the schema from the text
extracted_schema = await schema_extractor.run(text="Some text")
