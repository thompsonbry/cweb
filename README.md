# CWEB Project

## GraphRAG Integration

This project integrates with the GraphRAG Toolkit to build lexical graphs from documents.

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/thompsonbry/cweb.git
   cd cweb
   ```

2. Set up the environment:
   ```
   cp .env.example .env
   # Edit .env with your AWS and Neptune configuration
   ```

3. Link the GraphRAG Toolkit:
   ```
   mkdir -p lib
   ln -s /path/to/graphrag-toolkit/lexical-graph lib/graphrag-lexical-graph
   ```

### Usage

#### Building a Lexical Graph

To build a lexical graph from a text file:

```
python3 scripts/build_lexical_graph.py path/to/text/file.txt --document-id "document_id" --verbose
```

#### Querying a Lexical Graph

To query a lexical graph:

```
python3 scripts/query_lexical_graph.py "your query" --top-k 10 --output results.json --verbose
```

### Directory Structure

- `src/graphrag_integration/`: GraphRAG integration code
- `scripts/`: Utility scripts
- `test/data/`: Test data
- `lib/`: External libraries (linked)
