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

## Key Scripts

- `scripts/graphrag_fact_extractor.py`: Extracts facts from documents using GraphRAG
- `scripts/neptune_query_examples.py`: Demonstrates querying Neptune Analytics graphs
- `scripts/explore_neptune_graph.py`: Explores the schema of Neptune Analytics graphs

## Usage

To extract facts from a document:

```bash
uv run python scripts/graphrag_fact_extractor.py path/to/document.pdf --output output/facts.json
```

To query the Neptune Analytics graph:

```bash
uv run python scripts/neptune_query_examples.py --query "MATCH (e:Entity)-[r]->(o:Entity) RETURN e.name, type(r), o.name"
```

## Installation

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions, including how to install the GraphRAG toolkit.

## Current Status

See [TASKS.md](TASKS.md) for the current status of the project and next steps.

## Project Structure

See [PROJECT_FILES.md](PROJECT_FILES.md) for an overview of the project files and their purpose.
