# Includes

# load triples

# N Nodes

# N Relationships

# N Chunks

# N Incomplete Nodes

# N Incomplete Relationships

# N Suspected erroneous labels

# N Suspected duplicate nodes

# N Verbose relationship types

# [print(f"{node.label} | {node.properties['text']} | {node.id}") if 'text' in node.properties.keys() else print(f"{node.label} | {node.properties['matched_name']} | {node.properties['official_name']} | {node.properties['description']} | {node.id}") for node in triples.nodes ]
# [print(f"{rel.start_node_id} | {rel.type} | {rel.end_node_id}") for rel in triples.relationships]
