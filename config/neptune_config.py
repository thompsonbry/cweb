"""
Configuration for Neptune Analytics integration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Neptune Analytics configuration
NEPTUNE_ENDPOINT = os.getenv('NEPTUNE_ENDPOINT')
NEPTUNE_PORT = os.getenv('NEPTUNE_PORT', '8182')
NEPTUNE_AUTH_MODE = os.getenv('NEPTUNE_AUTH_MODE', 'IAM')  # 'IAM' or 'DEFAULT'
NEPTUNE_REGION = os.getenv('NEPTUNE_REGION', 'us-west-2')

# Vector configuration
VECTOR_DIMENSION = 1024  # Common embedding size
VECTOR_SIMILARITY_METRIC = "cosine"

# Graph configuration
GRAPH_NAMESPACE = "cweb"
EVIDENCE_LABEL = "Evidence"
ARGUMENT_LABEL = "Argument"
STORY_LABEL = "Story"
POSITION_LABEL = "Position"
ISSUE_LABEL = "Issue"

# Relationship types
SUPPORTS_REL = "SUPPORTS"
OPPOSES_REL = "OPPOSES"
PART_OF_REL = "PART_OF"
ADDRESSES_REL = "ADDRESSES"

def get_neptune_connection_string():
    """
    Returns the Neptune connection string based on configuration.
    
    Returns:
        str: Neptune connection string
    """
    if not NEPTUNE_ENDPOINT:
        raise ValueError("NEPTUNE_ENDPOINT environment variable is not set")
        
    if NEPTUNE_AUTH_MODE.upper() == 'IAM':
        return f"wss://{NEPTUNE_ENDPOINT}:{NEPTUNE_PORT}/gremlin"
    else:
        return f"ws://{NEPTUNE_ENDPOINT}:{NEPTUNE_PORT}/gremlin"

# HyperIBIS specific constants
ISSUE_TYPES = {
    'REGULAR': 'regular',
    'MUTEX': 'mutex',
    'HYPOTHESIS': 'hypothesis',
    'WORLD': 'world'
}

# Metacognition specific constants
CRITIQUE_TYPES = {
    'INCOMPLETENESS': 'incompleteness',
    'CONFLICT': 'conflict',
    'UNRELIABILITY': 'unreliability'
}

CORRECTION_TYPES = {
    'ELABORATION': 'elaboration',
    'REVISION': 'revision',
    'REJECTION': 'rejection'
}
