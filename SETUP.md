# Setup Guide for GraphRAG Integration

This guide provides detailed instructions for setting up the GraphRAG Toolkit integration with Neptune Analytics for the CWEB project.

## Prerequisites

1. AWS account with access to:
   - Amazon Bedrock
   - Neptune Analytics
   - IAM permissions for both services

2. Python 3.10+ environment (required by GraphRAG toolkit)
   - We recommend using `uv` for Python environment management

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/thompsonbry/cweb.git
cd cweb
```

### 2. Set up Python Environment with UV

```bash
# Install uv if not already installed
curl -sSf https://install.determinate.systems/uv | sh

# Create a virtual environment with Python 3.10
uv venv -p 3.10

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows
```

### 3. Install GraphRAG Toolkit

The GraphRAG Toolkit must be properly installed:

```bash
# Clone the GraphRAG Toolkit repository
git clone https://github.com/awslabs/graphrag-toolkit.git
cd graphrag-toolkit/lexical-graph

# Install the toolkit in development mode
uv pip install -e .

# Return to the project directory
cd ../../cweb
```

### 4. Install Project Dependencies

```bash
uv pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root with the following content:

```
# AWS Configuration
AWS_REGION=us-west-2
AWS_PROFILE=default

# Neptune Analytics Configuration
NEPTUNE_ANALYTICS_REGION=us-west-2
NEPTUNE_ANALYTICS_GRAPH_ID=g-k2n0lshd74

# Bedrock Configuration
BEDROCK_REGION=us-west-2
```

Adjust the values as needed for your environment.

### 6. Verify Installation

Run the following command to verify that the GraphRAG Toolkit is properly installed and configured:

```bash
uv run python -c "import graphrag_toolkit; print('GraphRAG Toolkit successfully imported')"
```

If you see "GraphRAG Toolkit successfully imported", the installation is correct.

## Running the Integration

### Extracting Facts from Documents

To extract facts from a document using GraphRAG and Neptune Analytics:

```bash
uv run python scripts/graphrag_fact_extractor.py path/to/document.pdf --output output/facts.json --verbose
```

### Querying Neptune Analytics Graph

To run example queries against the Neptune Analytics graph:

```bash
uv run python scripts/neptune_query_examples.py --verbose
```

For custom queries:

```bash
uv run python scripts/neptune_query_examples.py --query "MATCH (e:Entity) WHERE e.name CONTAINS 'R/M' RETURN e.id, e.name"
```

## Troubleshooting

### Python Version Issues

The GraphRAG Toolkit requires Python 3.10 or higher. If you're using an older version:

1. Ensure you're using `uv` with Python 3.10:
   ```bash
   uv venv -p 3.10
   ```

2. Verify your Python version:
   ```bash
   uv run python --version
   ```

### SQLite Issues

If you encounter SQLite version errors:

```bash
# Install pysqlite3-binary
uv pip install pysqlite3-binary

# Add this to the top of your scripts:
import pysqlite3
import sys
sys.modules['sqlite3'] = pysqlite3
```

### Neptune Analytics Connection Issues

If you encounter issues connecting to Neptune Analytics:

1. Verify your AWS credentials:
   ```bash
   aws sts get-caller-identity
   ```

2. Check that you have the necessary permissions for Neptune Analytics:
   ```bash
   aws neptune-graph describe-graph --graph-id g-k2n0lshd74 --region us-west-2
   ```

3. Ensure that the graph ID is correct in your `.env` file.

### Embedding Dimension Mismatch

If you encounter dimension mismatch errors:

1. Ensure you're using the correct embedding model:
   - Cohere: 1024 dimensions
   - Titan: 1536 dimensions

2. Update your configuration in the scripts:
   ```python
   GraphRAGConfig.embed_model = "cohere.embed-english-v3"
   GraphRAGConfig.embed_dimensions = 1024
   ```

## Additional Resources

- [GraphRAG Toolkit Documentation](https://github.com/awslabs/graphrag-toolkit)
- [Neptune Analytics Documentation](https://docs.aws.amazon.com/neptune/latest/userguide/analytics.html)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
