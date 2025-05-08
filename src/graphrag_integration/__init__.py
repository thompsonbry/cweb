"""
GraphRAG Toolkit integration for CWEB project.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the GraphRAG lexical-graph to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lib/graphrag-lexical-graph/src'))
