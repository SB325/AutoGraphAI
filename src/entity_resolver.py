from neo4j_graphrag.experimental.components.resolver import (
    SinglePropertyExactMatchResolver,
    # SpaCySemanticMatchResolver,
    # FuzzyMatchResolver,
)
import asyncio

resolver = SinglePropertyExactMatchResolver(driver)  # exact match resolver
# resolver = SpaCySemanticMatchResolver(driver)  # semantic match with spaCy
# resolver = FuzzyMatchResolver(driver)  # fuzzy match with RapidFuzz
res = await resolver.run()