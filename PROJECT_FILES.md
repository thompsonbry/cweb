# Project Files Overview

## Files in Use for GraphRAG Integration

### Core Project Files (Should be included in Git)

1. **`scripts/graphrag_fact_extractor.py`**
   - Main script for document processing with GraphRAG toolkit
   - Handles document loading, fact extraction, and graph building
   - Should be included in the project

2. **`tests/data/wcnn_1995.pdf`**
   - Test document used for fact extraction
   - Should be included in the project as test data

3. **`TASKS.md`**
   - Documentation of current status and next steps
   - Should be included in the project

4. **`requirements-graphrag.txt`**
   - Dependencies for GraphRAG toolkit integration
   - Should be included in the project

### Generated/Runtime Files (Should be excluded from Git)

1. **`bin/`**
   - Contains compiled binaries or scripts
   - Should be excluded from Git (added to .gitignore)

2. **`lib/`**
   - Contains library files that can be regenerated
   - Should be excluded from Git (added to .gitignore)

3. **`output.json`**
   - Generated output file from previous runs
   - Should be excluded from Git (added to .gitignore)

4. **`wcnn_facts.json`**
   - Generated facts from document processing
   - Should be excluded from Git (added to .gitignore)

5. **`/tmp/graphrag_output/`**
   - Temporary directory for GraphRAG processing
   - Should be excluded from Git (covered by /tmp/ in .gitignore)

6. **`/tmp/wcnn_1995_facts.json`**
   - Generated facts output in temporary directory
   - Should be excluded from Git (covered by /tmp/ in .gitignore)

7. **`.env`**
   - Contains environment-specific configuration
   - Should be excluded from Git (added to .gitignore)
   - An example template (.env.example) should be included instead

### External Resources (Not in Git)

1. **Neptune Analytics Graph (g-k2n0lshd74)**
   - AWS resource used for graph storage
   - Referenced by connection string in the code
   - Not a file, but an external resource

2. **AWS Bedrock Models**
   - Claude 3 Sonnet for LLM capabilities
   - Cohere embeddings for vector representations
   - Not files, but external services

## Notes on API Usage

The current implementation uses the following APIs:

- **GraphStoreFactory.for_graph_store()** - Used to create a graph store connected to Neptune Analytics
- **VectorStoreFactory.for_vector_store()** - Used to create a vector store connected to Neptune Analytics

For fact extraction, we'll need to implement:

- **execute_query()** - The correct API to query the Neptune Analytics graph
- ~~get_nodes(), get_edges(), query()~~ - These were hypothesized APIs that don't exist in the current implementation

## Next Steps for Checkpoint Commit

1. Clean up any debug code in graphrag_fact_extractor.py
2. Ensure .gitignore is properly configured
3. Document the current state in README.md
4. Commit the changes to create a checkpoint before implementing fact extraction
