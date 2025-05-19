# GraphRAG Integration Installation Guide

This guide provides detailed instructions for setting up the GraphRAG integration with Neptune Analytics.

## Prerequisites

- Python 3.10 or higher
- AWS CLI configured with appropriate permissions
- Access to Neptune Analytics (graph ID: g-k2n0lshd74 in us-west-2)
- Access to Amazon Bedrock (for embeddings and LLM)

## Installation Steps

### 1. Install uv (Python package manager)

```bash
curl -sSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone the repository

```bash
git clone https://github.com/thompsonbry/cweb.git
cd cweb
git checkout graphrag-integration
```

### 3. Create a Python 3.10 virtual environment

```bash
uv venv -p 3.10
```

### 4. Install dependencies

```bash
uv pip install -r requirements.txt -r requirements-graphrag.txt
```

### 5. Install GraphRAG toolkit

The GraphRAG toolkit is not available as a standard pip package. You need to install it from the AWS Labs GitHub repository:

```bash
git clone https://github.com/awslabs/graphrag.git
cd graphrag
uv pip install -e .
cd ..
```

### 6. Configure environment variables

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

## Verification

To verify that the installation is working correctly, run:

```bash
uv run python scripts/neptune_query_examples.py --verbose
```

This should connect to Neptune Analytics and display query results.

## Troubleshooting

### Common Issues

1. **GraphRAG toolkit not found**:
   - Make sure you've installed the GraphRAG toolkit from the AWS Labs GitHub repository
   - Verify that you're using Python 3.10 or higher

2. **Neptune Analytics connection issues**:
   - Check that your AWS credentials have access to Neptune Analytics
   - Verify that the graph ID in your .env file is correct

3. **Bedrock throttling errors**:
   - These are normal when making many requests in succession
   - The implementation includes retry logic with backoff strategies
   - Consider adding delays between processing multiple documents

### Getting Help

If you encounter issues not covered in this guide, please:
1. Check the AWS documentation for GraphRAG toolkit
2. Review the Neptune Analytics documentation
3. Open an issue in the project repository with detailed error information
