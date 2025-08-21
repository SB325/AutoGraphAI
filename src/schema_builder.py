from neo4j_graphrag.experimental.components.schema import (
    SchemaBuilder,
    NodeType,
    PropertyType,
    RelationshipType,
    SchemaFromTextExtractor,
)
from pydantic import BaseModel
from typing import List

from neo4j_graphrag.llm import OllamaLLM
import asyncio
import json
from uuid import uuid

class property_template(BaseModel):
    name: str 
    type: str 

class triple_template(BaseModel):
    subject_label: str 
    predicate_label: str 
    object_label: str 

class node_template(BaseModel):
    label: str 
    properties: List[property_template]
    id_: uuid.UUID

class edge_template(BaseModel):
    label: str 
    id_: uuid.UUID

class pattern_template(BaseModel):
    pattern: List[triple_template]

# ==================
class schema_builder():
    def __init__(self):
        self.schema_builder = SchemaBuilder()

        self.chunk: str = None
        self.full_node_list: List[node_template]
        self.full_edge_list: List[edge_template]
        self.full_pattern_list: List[pattern_template]

        self.temp_node_list: List[node_template]
        self.temp_edge_list: List[edge_template]
        self.temp_pattern_list: List[pattern_template]

    def add_node(self, node_obj: node_template):
        node_dict = node_obj.model_dump()
        self.temp_node_list.append(node_dict)

    def remove_node(self, node_id: str | List):
        index_to_remove = [cnt, _ for cnt, _ in enumerate(self.temp_node_list) if val['id_'] == node_id]

        if index_to_remove:
            self.temp_node_list.pop(index_to_remove.reverse())

    def add_edge(self, edge_obj: edge_template):
        edge_dict = edge_obj.model_dump()
        self.temp_edge_list.append(edge_dict)

    def remove_edge(self, edge_id: str | List):
        index_to_remove = [cnt, _ for cnt, _ in enumerate(self.temp_edge_list) if val['id_'] == edge_id]

        if index_to_remove:
            self.temp_edge_list.pop(index_to_remove.reverse())

    def add_pattern(self, pattern_obj: pattern_template):
        pattern_dict = pattern_obj.model_dump()
        self.temp_pattern_list.append(pattern_dict)

    def validate_fact(self):
        # consolidate properties among nodes with same name if user verifies.
        # else, have user rename one or both nodes with their properties retained.
        node_labels = {cnt: node['label'] for cnt, node in enumerate(self.temp_node_list)}
        unique_labels = list(set([node_labels[cnt] for cnt in range(len(self.temp_node_list))])

        if len(unique_labels) != len(self.temp_node_list)
            # contains duplicate label
            match_groups = []
            node_label_values = node_labels.values()
            for ul in unique_labels:
                if node_label_values.count(ul) > 1:
                    match_index = []
                    while True:
                        try:
                            index = node_label_values.index(ul)
                        except:
                            break
                        match_index.append(index)
                    match_groups.append(match_index)
            if match_groups:
                print(f"Duplicate nodes detected:")
                for cnt, mat in enumerate(match_groups):
                    print(f"Duplicate node {cnt}:")
                    print(f"{json.dumps([ma for ma in self.temp_node_list 
                            if ma['label'] in node_label_values[mat]])}")
                nodes_to_remove = []
                while True:
                    val = input(f"Would you like to:\n\t- 1. Consolidate their properties?\n\t- 2. Relabel them and keep them separate?")
                    if val not in ['1', '2']:
                        print("Please enter a value of '1' or '2'.")
                    else:
                        duplicated_nodes = [lab for lab in node_labels if lab.keys()[0] in mat]
                        if val == '1':
                            consolidated_node = duplicated_nodes[0]
                            # Consolidate properties among the nodes
                            for dn in duplicated_nodes[1:]:
                                if consolidated_node['label'] not in dn['label']:
                                    BaseException('This cannot happen. Must be duplicates here.')
                                if dn['properties']['name'] not in 
                                    [prop['name']  for prop in consolidated_node['properties']]
                                        != :
                                    consolidated_node['properties'].append(dn['properties'])
                            # remove all but the first value of duplicated_nodes (index)
                            # from self.temp_node_list
                            nodes_to_remove.extend(duplicated_nodes[1:])
                            for ind in nodes_to_remove.reverse():
                                self.temp_node_list.pop(ind)  
                            break

                        elif val == '2':
                            for cnt, dup in enumerate(duplicated_nodes):
                                newname = input(f"Enter new label of duplicate {cnt} (Leave empty to keep):")
                                if val:
                                    while True:
                                        val = input(f"Are you sure you want to change the label of node:\n" \
                                            + f"{json.dumps(self.temp_node_list[dup])}\nto\n" \
                                            + f"{newname} ?")
                                        if 'y' in val.lower() or 'yes' in val.lower():
                                            self.temp_node_list[dup]['label'] = newname
                                            break
                                        if 'n' in val.lower() or 'no' in val.lower():
                                            break
                                        else:
                                            print("Please answer 'Y' (or Yes) or 'N' (or No).")

        # remove duplicate edges
        edges = list(set([edge['label'] for edge in self.temp_edge_list])
        edge_dicts = [{ 'label':] ed } for ed in edges]
        self.temp_edge_list = edge_dicts

        # remove duplicate patterns
        to_remove = []
        subjects = [{cnt, pat['subject_label']} for cnt, pat in enumerate(self.temp_pattern_list)]:
        
        if subjects:
            unique_subjects = list(set([val.values()[0] for val in subjects]))
            for unisub in unique_subjects:
                predicates = [{cnt2, subpat['predicate_label'] for cnt2, subpat in enumerate(self.temp_pattern_list) if unisub == subpat['subject_label']}]
                if predicates:
                    unique_predicates = list(set([val.values()[0] for val in predicates]))
                    for unipred in unique_predicates:
                        objects_ = [{cnt3, pat['object_label'] in cnt3, predpat in enumerate(self.temp_pattern_list) if unipred == predpat['predicate_label']}]
                        # duplicates in objects_ values list mean that cnt3 values are fact duplicate indeces.
                        obj_list = [val.values()[0] for val in objects_]
                        unique_objects = list(set(obj_list))
                        for uo in unique_objects:
                            if obj_list.count(uo) > 1:
                                to_remove.append([obj.keys()[0] for obj in objects_ if uo in obj.values()[0]][1:])
            
            if to_remove:
                sorted_indeces = to_remove.sort(reverse=True)
                for si in sorted_indeces:
                    self.temp_pattern_list.pop(si)

    def add_fact_to_schema(self):
        self.temp_node_list: List[node_template]
        self.temp_edge_list: List[edge_template]
        self.temp_pattern_list: List[pattern_template]
        await schema_builder.run(
            node_types=[
                NodeType(
                    label=val['label'],
                    properties=[
                        PropertyType(**props)
                        for props in val['properties']
                    ],
                ) for val in self.temp_node_list
            ],
            relationship_types=[
                RelationshipType(
                    val['label'],
                ) for val in self.temp_edge_list
            ],
            patterns=[
                (val['subject_label'], 
                val['predicate_label'], 
                val['object_label']) for val in self.temp_pattern_list
            ],
        )
