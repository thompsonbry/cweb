# Project Files Structure

This document provides an overview of the key files and directories in the CWEB project, focusing on the GraphRAG integration with Neptune Analytics.

## Directory Structure

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

## Key Files

### Scripts

- **graphrag_fact_extractor.py**: Main script for extracting facts from documents using GraphRAG and Neptune Analytics. It processes documents, builds a graph, and extracts structured facts.

- **neptune_query_examples.py**: Demonstrates various query patterns for extracting information from Neptune Analytics graphs using OpenCypher.

- **explore_neptune_graph.py**: Utility script to explore the schema and content of a Neptune Analytics graph.

- **graphrag_example.py**: Simple example showing how to use the GraphRAG toolkit.

### Configuration

- **.env.example**: Template for environment variables needed for the project, including AWS region, Neptune Analytics graph ID, etc.

- **requirements.txt**: List of Python dependencies for the project.

- **requirements-graphrag.txt**: GraphRAG-specific dependencies.

### Documentation

- **SETUP.md**: Detailed instructions for setting up the project, including GraphRAG toolkit installation and Neptune Analytics configuration.

- **README.md**: Overview of the project, its purpose, and basic usage instructions.

## Usage Examples

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
