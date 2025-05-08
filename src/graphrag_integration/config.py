"""
Configuration for GraphRAG Toolkit integration.
"""

import os
import boto3
from typing import Dict, Any, Tuple

# GraphRAG configuration
GRAPHRAG_CONFIG = {
    "bedrock": {
        "region": os.environ.get("AWS_REGION", "us-east-1"),
        "embedding_model": "amazon.titan-embed-text-v1",
        "llm_model": "anthropic.claude-3-sonnet-20240229-v1:0"
    },
    "neptune": {
        "endpoint": os.environ.get("NEPTUNE_ENDPOINT", ""),
        "port": int(os.environ.get("NEPTUNE_PORT", "8182")),
        "use_iam_auth": os.environ.get("NEPTUNE_USE_IAM_AUTH", "true").lower() == "true",
        "region": os.environ.get("AWS_REGION", "us-east-1")
    },
    "lexical_graph": {
        "namespace": "cweb",
        "chunk_size": 512,
        "chunk_overlap": 128,
        "max_tokens_per_chunk": 512
    }
}

def get_bedrock_client():
    """
    Get a Bedrock client.
    
    Returns:
        boto3.client: The Bedrock client
    """
    region = GRAPHRAG_CONFIG["bedrock"]["region"]
    return boto3.client("bedrock-runtime", region_name=region)

def get_neptune_connection_info() -> Tuple[str, int, bool, str]:
    """
    Get Neptune connection information.
    
    Returns:
        Tuple[str, int, bool, str]: The Neptune endpoint, port, IAM auth flag, and region
    """
    endpoint = GRAPHRAG_CONFIG["neptune"]["endpoint"]
    port = GRAPHRAG_CONFIG["neptune"]["port"]
    use_iam_auth = GRAPHRAG_CONFIG["neptune"]["use_iam_auth"]
    region = GRAPHRAG_CONFIG["neptune"]["region"]
    
    return endpoint, port, use_iam_auth, region
