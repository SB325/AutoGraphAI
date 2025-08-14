from neo4j_graphrag.experimental.components.schema import (
    SchemaBuilder,
    NodeType,
    PropertyType,
    RelationshipType,
)
import asyncio

schema_builder = SchemaBuilder()

await schema_builder.run(
    node_types=[
        NodeType(
            label="Person",
            properties=[
                PropertyType(name="name", type="STRING"),
                PropertyType(name="place_of_birth", type="STRING"),
                PropertyType(name="date_of_birth", type="DATE"),
            ],
        ),
        NodeType(
            label="Organization",
            properties=[
                PropertyType(name="name", type="STRING"),
                PropertyType(name="country", type="STRING"),
            ],
        ),
    ],
    relationship_types=[
        RelationshipType(
            label="WORKED_ON",
        ),
        RelationshipType(
            label="WORKED_FOR",
        ),
    ],
    patterns=[
        ("Person", "WORKED_ON", "Field"),
        ("Person", "WORKED_FOR", "Organization"),
    ],
)