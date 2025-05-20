# CWEB Project

## Overview

This project integrates with the AWSLabs GraphRAG toolkit for fact extraction from documents. It uses Neptune Analytics for graph storage and AWS Bedrock for embeddings and LLM capabilities.

## Key Features

- Document processing with GraphRAG toolkit
- Knowledge graph building in Neptune Analytics
- Fact extraction using OpenCypher queries
- Integration with Amazon Bedrock for embeddings and LLM

## Environment Setup

This project uses `uv` to manage Python environments. Python 3.10+ is required for compatibility with the GraphRAG toolkit.

```bash
# Create and activate Python environment
uv venv -p 3.10
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
uv pip install -r requirements-graphrag.txt
```

## GraphRAG Integration

The project integrates with the AWSLabs GraphRAG toolkit for fact extraction from documents. Key components include:

- **GraphRAG Toolkit**: Official AWSLabs implementation requiring Python 3.10+
- **AWS Services**: 
  - Amazon Bedrock for embeddings (Cohere) and LLM (Claude 3 Sonnet)
  - Neptune Analytics for graph storage (graph ID: g-k2n0lshd74 in us-west-2)
- **Test Documents**: Located in `tests/data` directory

## Project Structure

### Directory Structure

```
cweb/
├── scripts/                  # Executable scripts
│   ├── graphrag_fact_extractor.py    # Main script for extracting facts using GraphRAG
│   ├── neptune_query_examples.py     # Examples of querying Neptune Analytics
│   ├── explore_neptune_graph.py      # Script to explore Neptune Analytics graph schema
│   └── graphrag_example.py           # Example usage of GraphRAG toolkit
├── tests/                    # Test files and data
│   └── data/                 # Test documents
│       ├── wcnn_1995.pdf     # Sample PDF document
│       └── WCNN_1995_Summary.md  # Summary of the document
├── src/                      # Source code
│   └── graphrag_integration/ # GraphRAG integration code
│       ├── __init__.py
│       ├── config.py         # Configuration for GraphRAG
│       └── neptune_analytics_adapter.py  # Adapter for Neptune Analytics
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
├── requirements-graphrag.txt # GraphRAG-specific dependencies
└── SETUP.md                  # Setup instructions
```

### Key Scripts

- **graphrag_fact_extractor.py**: Main script for extracting facts from documents using GraphRAG and Neptune Analytics. It processes documents, builds a graph, and extracts structured facts.

- **neptune_query_examples.py**: Demonstrates various query patterns for extracting information from Neptune Analytics graphs using OpenCypher.

- **explore_neptune_graph.py**: Utility script to explore the schema and content of a Neptune Analytics graph.

- **graphrag_example.py**: Simple example showing how to use the GraphRAG toolkit.

### Configuration

- **.env.example**: Template for environment variables needed for the project, including AWS region, Neptune Analytics graph ID, etc.

- **requirements.txt**: List of Python dependencies for the project.

- **requirements-graphrag.txt**: GraphRAG-specific dependencies.

## Usage

### Extracting Facts from Documents

```bash
uv run python scripts/graphrag_fact_extractor.py tests/data/wcnn_1995.pdf --output output/wcnn_facts.json --verbose
```

### Querying Neptune Analytics Graph

```bash
uv run python scripts/neptune_query_examples.py --verbose
```

### Running Custom Queries

```bash
uv run python scripts/neptune_query_examples.py --query "MATCH (e:Entity) WHERE e.name CONTAINS 'R/M' RETURN e.id, e.name"
```

### Exploring Graph Schema

```bash
uv run python scripts/explore_neptune_graph.py --output /tmp/graph_schema.json
```

## Installation

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions, including how to install the GraphRAG toolkit.

## Current Status

See [TASKS.md](TASKS.md) for the current status of the project and next steps.

## Development Guidelines

See [DEVELOPMENT.md](DEVELOPMENT.md) and [DEVELOPMENT_GUIDELINES.md](DEVELOPMENT_GUIDELINES.md) for information on development practices and guidelines for this project.
