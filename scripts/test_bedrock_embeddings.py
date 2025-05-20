#!/usr/bin/env python3
"""
Test Bedrock embeddings with Neptune Analytics.
"""

import os
import sys
import json
import boto3
import argparse
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_neptune_analytics_endpoint():
    """
    Get the Neptune Analytics endpoint from the graph ID.
    
    Returns:
        str: The Neptune Analytics endpoint
    """
    graph_id = os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID")
    if not graph_id:
        raise ValueError("NEPTUNE_ANALYTICS_GRAPH_ID environment variable is required")
    
    region = os.environ.get("NEPTUNE_ANALYTICS_REGION", "us-west-2")
    return f"{graph_id}.{region}.neptune-graph.amazonaws.com"

def get_bedrock_client():
    """
    Get a Bedrock client.
    
    Returns:
        boto3.client: The Bedrock client
    """
    region = os.environ.get("AWS_REGION", "us-west-2")
    return boto3.client("bedrock-runtime", region_name=region)

def get_cohere_embeddings(text, client=None):
    """
    Get Cohere embeddings for a text.
    
    Args:
        text (str): The text to embed
        client (boto3.client, optional): The Bedrock client
        
    Returns:
        list: The embeddings
    """
    if client is None:
        client = get_bedrock_client()
    
    # Prepare request body
    request_body = {
        "texts": [text],
        "input_type": "search_document",
        "truncate": "NONE"
    }
    
    # Invoke Bedrock
    response = client.invoke_model(
        modelId="cohere.embed-english-v3",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(request_body)
    )
    
    # Parse response
    response_body = json.loads(response["body"].read())
    embeddings = response_body.get("embeddings", [])[0]
    
    return embeddings

def test_bedrock_embeddings(text, verbose=False):
    """
    Test Bedrock embeddings with Neptune Analytics.
    
    Args:
        text (str): The text to embed
        verbose (bool, optional): Enable verbose output
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get Bedrock client
        logger.info("Initializing Bedrock client...")
        bedrock_client = get_bedrock_client()
        
        # Get Cohere embeddings
        logger.info("Getting Cohere embeddings...")
        embeddings = get_cohere_embeddings(text, bedrock_client)
        
        if verbose:
            logger.info(f"Embeddings dimension: {len(embeddings)}")
            logger.info(f"First 5 values: {embeddings[:5]}")
        
        # Get Neptune Analytics endpoint
        logger.info("Getting Neptune Analytics endpoint...")
        graph_endpoint = get_neptune_analytics_endpoint()
        
        logger.info(f"Neptune Analytics endpoint: {graph_endpoint}")
        logger.info("Test completed successfully")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing Bedrock embeddings: {str(e)}")
        if verbose:
            import traceback
            logger.error(traceback.format_exc())
        return False

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Test Bedrock embeddings with Neptune Analytics")
    parser.add_argument("--text", "-t", default="This is a test text for Cohere embeddings.", help="Text to embed")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if test_bedrock_embeddings(args.text, args.verbose):
        logger.info("Test completed successfully")
        sys.exit(0)
    else:
        logger.error("Test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
