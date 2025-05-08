# Setup Guide for GraphRAG Integration

This guide provides detailed instructions for setting up the GraphRAG Toolkit integration with Neptune Analytics for the CWEB project.

## Prerequisites

1. AWS account with access to:
   - Amazon Bedrock
   - Neptune Analytics
   - IAM permissions for both services

2. Python 3.7+ environment

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/thompsonbry/cweb.git
cd cweb
```

### 2. Install GraphRAG Toolkit

The GraphRAG Toolkit must be properly installed and linked. Follow these steps:

```bash
# Clone the GraphRAG Toolkit repository
git clone https://github.com/aws-samples/graphrag-toolkit.git
cd graphrag-toolkit

# Install the lexical-graph module
cd lexical-graph
pip install -e .
cd ..

# Return to the cweb project directory
cd ../cweb

# Create a symbolic link to the GraphRAG Toolkit
mkdir -p lib
ln -s $(realpath ../graphrag-toolkit/lexical-graph) lib/graphrag-lexical-graph
```

### 3. Install Project Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following content:

```
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# Neptune Analytics Configuration
NEPTUNE_ANALYTICS_REGION=us-west-2
NEPTUNE_ANALYTICS_GRAPH_ID=g-k2n0lshd74
```

Adjust the values as needed for your environment.

### 5. Verify Installation

Run the following command to verify that the GraphRAG Toolkit is properly installed and configured:

```bash
python -c "import sys; sys.path.append('./lib/graphrag-lexical-graph/src'); import graphrag_toolkit; print('GraphRAG Toolkit successfully imported')"
```

If you see "GraphRAG Toolkit successfully imported", the installation is correct.

## Troubleshooting

### Import Errors

If you encounter import errors related to the GraphRAG Toolkit:

1. Verify that the symbolic link is correct:
   ```bash
   ls -la lib/graphrag-lexical-graph
   ```

2. Check that the GraphRAG Toolkit is installed:
   ```bash
   cd lib/graphrag-lexical-graph
   pip install -e .
   cd ../..
   ```

3. Verify Python path:
   ```bash
   python -c "import sys; print(sys.path)"
   ```
   Ensure that the path to the GraphRAG Toolkit is included.

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

## Running the Integration

### Building a Lexical Graph

To build a lexical graph from a text file:

```bash
python scripts/build_lexical_graph.py path/to/text/file.txt --document-id "document_id" --verbose
```

### Querying a Lexical Graph

To query a lexical graph:

```bash
python scripts/query_lexical_graph.py "your query" --top-k 10 --output results.json --verbose
```

## Additional Resources

- [GraphRAG Toolkit Documentation](https://github.com/aws-samples/graphrag-toolkit)
- [Neptune Analytics Documentation](https://docs.aws.amazon.com/neptune/latest/userguide/analytics.html)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
