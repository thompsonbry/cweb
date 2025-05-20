# Setup Guide for GraphRAG Integration

This guide provides detailed instructions for setting up the GraphRAG Toolkit integration with Neptune Analytics for the CWEB project.

## Prerequisites

1. AWS account with access to:
   - Amazon Bedrock
   - Neptune Analytics
   - IAM permissions for both services

2. Development environment:
   - Python 3.10 or higher
   - `uv` for Python environment management
   - AWS CLI configured with appropriate credentials

## Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/thompsonbry/cweb.git
   cd cweb
   ```

2. **Set up Python environment using `uv`**:
   ```bash
   # Create and activate Python environment
   uv venv -p 3.10
   source .venv/bin/activate

   # Install dependencies
   uv pip install -r requirements.txt
   ```

3. **Install GraphRAG Toolkit**:
   ```bash
   # Clone the GraphRAG Toolkit repository
   git clone https://github.com/aws-samples/graphrag-toolkit.git ~/github/graphrag-toolkit

   # Install the lexical-graph package
   cd ~/github/graphrag-toolkit/lexical-graph
   pip install -e .

   # Install the document-processing package
   cd ~/github/graphrag-toolkit/document-processing
   pip install -e .
   ```

4. **Install additional dependencies**:
   ```bash
   # Install GraphRAG-specific dependencies
   uv pip install -r requirements-graphrag.txt
   ```

## AWS Configuration

1. **Configure AWS CLI**:
   ```bash
   aws configure
   ```
   Enter your AWS Access Key ID, Secret Access Key, and default region (us-west-2).

2. **Set up environment variables**:
   Create a `.env` file in the project root with the following content:
   ```
   # AWS Configuration
   AWS_REGION=us-west-2
   AWS_PROFILE=default

   # Neptune Analytics Configuration
   NEPTUNE_ANALYTICS_REGION=us-west-2
   NEPTUNE_ANALYTICS_GRAPH_ID=your-graph-id-here

   # S3 Configuration for GraphRAG
   S3_BUCKET=your-bucket-name
   S3_PREFIX=lexical-graphs
   ```
   
   Replace `your-graph-id-here` with your Neptune Analytics graph ID and `your-bucket-name` with your S3 bucket name.

## Verify Installation

1. **Test Neptune Analytics connection**:
   ```bash
   uv run python scripts/neptune_query_examples.py --verbose
   ```

2. **Test GraphRAG integration**:
   ```bash
   uv run python scripts/graphrag_example.py
   ```

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Ensure your AWS credentials are valid and not expired
   - Verify you have the necessary permissions for Neptune Analytics and Bedrock

2. **GraphRAG Import Errors**:
   - Verify that GraphRAG Toolkit is installed correctly
   - Check that you're using Python 3.10 or higher

3. **Throttling Errors from Bedrock**:
   - These are expected and handled with retries
   - For large documents, processing may take longer due to throttling

4. **Neptune Analytics Connection Issues**:
   - Verify the graph ID is correct in your .env file
   - Ensure your IAM role has access to the Neptune Analytics graph

### Getting Help

If you encounter issues not covered here, please:
1. Check the AWS documentation for Neptune Analytics and Bedrock
2. Review the GraphRAG Toolkit documentation
3. Open an issue in the project repository with detailed error information
