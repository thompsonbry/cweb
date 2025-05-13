# CWEB Project

## Overview

This project integrates with the AWSLabs GraphRAG toolkit for fact extraction from documents. It uses Neptune Analytics for graph storage and AWS Bedrock for embeddings and LLM capabilities.

## Environment Setup

This project uses `uv` to manage Python environments. Python 3.10 is properly configured and available through `uv`.

```bash
# Create and activate Python environment
uv venv
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

## Running the Scripts

```bash
# Process a document with GraphRAG
cd ~/github/cweb
uv run python scripts/graphrag_fact_extractor.py tests/data/wcnn_1995.pdf --output output/wcnn_facts.json
```

## Current Status

See [TASKS.md](TASKS.md) for the current status of the project and next steps.

## Project Structure

See [PROJECT_FILES.md](PROJECT_FILES.md) for an overview of the project files and their purpose.
