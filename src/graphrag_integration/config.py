"""
Configuration for GraphRAG Toolkit integration with Neptune Analytics.
"""

import os
from dotenv import load_dotenv
from config.neptune_config import (
    NEPTUNE_ENDPOINT, 
    NEPTUNE_PORT, 
    NEPTUNE_AUTH_MODE, 
    NEPTUNE_REGION,
    VECTOR_DIMENSION
)

# Load environment variables
load_dotenv()

# GraphRAG Lexical Graph Configuration
GRAPHRAG_CONFIG = {
    # Neptune Analytics Configuration
    "neptune": {
        "endpoint": NEPTUNE_ENDPOINT,
        "port": NEPTUNE_PORT,
        "auth_mode": NEPTUNE_AUTH_MODE,
        "region": NEPTUNE_REGION,
        "vector_dimension": VECTOR_DIMENSION,
    },
    
    # AWS Bedrock Configuration for embeddings and LLMs
    "bedrock": {
        "region": os.getenv("AWS_REGION", "us-west-2"),
        "embedding_model": os.getenv("BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v1"),
        "llm_model": os.getenv("BEDROCK_LLM_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0"),
    },
    
    # Lexical Graph Configuration
    "lexical_graph": {
        "namespace": "cweb",
        "chunk_size": 512,
        "chunk_overlap": 50,
        "max_tokens_per_chunk": 256,
    },
    
    # Document Processing Configuration
    "document_processing": {
        "upload_dir": os.getenv("DOCUMENT_UPLOAD_DIR", "/local/home/bryant/github/cweb/data/documents"),
        "processed_dir": os.getenv("DOCUMENT_PROCESSED_DIR", "/local/home/bryant/github/cweb/data/processed"),
    }
}

def get_neptune_connection_info():
    """
    Returns the Neptune connection information in the format expected by GraphRAG.
    """
    from config.neptune_config import get_neptune_connection_string
    
    connection_string = get_neptune_connection_string()
    protocol = "wss://" if NEPTUNE_AUTH_MODE == "IAM" else "ws://"
    
    return {
        "endpoint": NEPTUNE_ENDPOINT,
        "port": NEPTUNE_PORT,
        "connection_string": connection_string,
        "auth_mode": NEPTUNE_AUTH_MODE,
        "region": NEPTUNE_REGION,
        "protocol": protocol,
    }

def get_bedrock_client():
    """
    Returns a configured Bedrock client.
    """
    import boto3
    
    region = GRAPHRAG_CONFIG["bedrock"]["region"]
    return boto3.client("bedrock-runtime", region_name=region)

def get_bedrock_embedding_model():
    """
    Returns the Bedrock embedding model ID.
    """
    return GRAPHRAG_CONFIG["bedrock"]["embedding_model"]

def get_bedrock_llm_model():
    """
    Returns the Bedrock LLM model ID.
    """
    return GRAPHRAG_CONFIG["bedrock"]["llm_model"]
