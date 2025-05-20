# CWEB Project Tasks

## Completed Tasks

### GraphRAG Integration
- ✅ Set up GraphRAG toolkit integration
- ✅ Connected to Neptune Analytics graph in us-west-2
- ✅ Implemented fact extraction from documents
- ✅ Created Neptune Analytics adapter
- ✅ Tested with sample documents

### Documentation
- ✅ Created installation guide
- ✅ Updated README with project structure
- ✅ Added development guidelines
- ✅ Documented Neptune Analytics integration

### Testing
- ✅ Tested document processing with GraphRAG
- ✅ Verified Neptune Analytics connection
- ✅ Tested OpenCypher queries
- ✅ Validated fact extraction results

## Current Tasks

### GraphRAG Enhancements
- [ ] Implement batch processing for multiple documents
- [ ] Add support for additional document types
- [ ] Improve error handling and retries for Bedrock throttling
- [ ] Optimize embedding generation for large documents

### Neptune Analytics Integration
- [ ] Enhance graph schema for better querying
- [ ] Implement more sophisticated OpenCypher queries
- [ ] Add support for vector search in Neptune Analytics
- [ ] Create visualization tools for the knowledge graph

### Research
- [ ] Investigate nanopublications format
- [ ] Research alignment with HyperIBIS model
- [ ] Explore argument extraction techniques
- [ ] Evaluate different embedding models for fact extraction

## Future Tasks

### User Interface
- [ ] Create Jupyter notebooks for interactive exploration
- [ ] Develop simple web interface for querying the graph
- [ ] Add visualization components for knowledge graphs

### Evaluation
- [ ] Develop metrics for fact extraction quality
- [ ] Compare with other RAG approaches
- [ ] Evaluate performance on different document types
- [ ] Measure query performance and accuracy

## Technical Details

### Environment
- Using Python 3.10+ with uv for environment management
- Neptune Analytics in us-west-2 region
- Amazon Bedrock for embeddings and LLM capabilities

### Key Components
- GraphRAG toolkit from AWS Labs
- Cohere embeddings with 1024 dimensions
- Claude 3 Sonnet for LLM capabilities
- Neptune Analytics for graph storage
