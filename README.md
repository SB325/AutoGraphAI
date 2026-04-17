# AutoGraphAI
Automatic generation of Knowledge Graphs and Ontologies from unstructured text to support robust Agentic context compression using Graph RAG.

### 1. Purpose
Agentic workflows generate a large ammount of context as the complexity of tasks increase. Models must perform inference on this context in order to perform their task, 
which greatly relies on the ability to squeeze the most relevant information into their context windows before data is dropped from it. This project rests on the bet that
*knowledge graphs will unlock the key to long term conversational and agentic context maintenance at scale*.

### 2. Context compression and Memory management
Context compression through generative summarization only delays the inevitable. The only solution thus far has been to increase the number of sub-agents while decreasing 
their scope. Efficient context compression greatly increases the lifetime of an agent before it forgets or hallucinates context.

### 3. Benefits
Knowledge graphs ground LLMs through deterministic relationships between entities (nouns) and are derived directly from human verified knowledge rather than probablstic 
modeling. RAG chunks embed combined context from entire paragraphs, while node-edge chunks embed context more granularly at the N-gram token level. KG retrieval comes after 
multi-hop graph traversal which:

- greatly decreases the likelihood of hallucination
- enables multi-hop reasoning for improved zero shot inference
- represents context with minimal token redundancy
- is natively understood by LLMs
