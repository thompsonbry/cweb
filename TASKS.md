# GraphRAG Integration Tasks

## Current Status

We've successfully integrated the GraphRAG toolkit with Neptune Analytics and fixed the dimension mismatch error. The document processing pipeline is now working end-to-end.

### What's Working
- Successfully installed and configured the GraphRAG toolkit
- Connected to Neptune Analytics graph (g-k2n0lshd74 in us-west-2)
- Document loading and parsing is working correctly
- Proposition extraction is working (36 nodes processed)
- Topic extraction is working (36 nodes processed)
- Graph building is working (1240 nodes/edges created)
- Vector index building is working
- Data is successfully stored in Neptune Analytics

### Current Issue
While the document processing pipeline is working, we still need to implement proper fact extraction from the Neptune Analytics graph. The current implementation doesn't have access to methods for retrieving nodes and edges directly.

### Next Steps
1. Implement proper fact extraction from Neptune Analytics:
   - Research Neptune Analytics query API
   - Implement Gremlin or openCypher queries to retrieve facts from the graph
   - Extract entities and relationships from the query results
   - Test with additional documents from the test data directory
   - Explore a visualization of the extracted facts with a notebook.
2. Read and summarize nanopublications. How does this relate to the HyperIBIS model and the proposed schema? Can we align with nanopublications? What are the gaps?
3. Extend things in this project to also extract arguments from those documents.

## Implementation Details

### GraphRAG Configuration
- Using Neptune Analytics for graph storage (g-k2n0lshd74 in us-west-2)
- Using Cohere embeddings (cohere.embed-english-v3) with 1024 dimensions
- Using AWS Bedrock for LLM capabilities (Claude 3 Sonnet)

### Script Structure
- `graphrag_fact_extractor.py`: Main script for document processing
- Document processing pipeline:
  1. Load and parse document
  2. Extract propositions (36 nodes processed)
  3. Extract topics (36 nodes processed)
  4. Build graph (1240 nodes/edges created)
  5. Build vector index
  6. Extract facts from graph (needs implementation)

### AWS Resources
- Neptune Analytics Graph ID: g-k2n0lshd74
- Region: us-west-2
- Bedrock models:
  - LLM: anthropic.claude-3-sonnet-20240229-v1:0
  - Embeddings: cohere.embed-english-v3 (1024 dimensions)

## Technical Notes

The Neptune Analytics graph store doesn't expose direct methods for retrieving nodes and edges. We need to implement proper querying using the Neptune Analytics API. The graph store is of type `NeptuneAnalyticsClient` which likely supports Gremlin or openCypher queries.

Available methods on the graph_index object:
```
['allow_batch_inference', 'build', 'extract', 'extract_and_build', 'extraction_components', 'extraction_dir', 'extraction_pre_processors', 'graph_store', 'indexing_config', 'tenant_id', 'vector_store']
```
