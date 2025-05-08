"""
Neptune adapter for GraphRAG Toolkit integration.
"""

import os
import sys
import logging
from typing import Optional

# Add the GraphRAG lexical-graph to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lib/graphrag-lexical-graph/src'))

# Import GraphRAG components
try:
    from graphrag_toolkit.lexical_graph.graph.neptune_graph import NeptuneGraph
    from graphrag_toolkit.lexical_graph.graph.neptune_vector_store import NeptuneVectorStore
except ImportError:
    raise ImportError(
        "Failed to import GraphRAG Toolkit. Make sure the lexical-graph module "
        "is properly linked in the lib directory."
    )

from src.graphrag_integration.config import GRAPHRAG_CONFIG, get_neptune_connection_info

logger = logging.getLogger(__name__)

class NeptuneAdapter:
    """
    Neptune adapter for CWEB project using GraphRAG Toolkit.
    """
    
    def __init__(self):
        """
        Initialize the Neptune adapter.
        """
        self.config = GRAPHRAG_CONFIG
        self.namespace = self.config["lexical_graph"]["namespace"]
        
        # Get Neptune connection info
        endpoint, port, use_iam_auth, region = get_neptune_connection_info()
        
        # Initialize Neptune graph
        self.graph = NeptuneGraph(
            endpoint=endpoint,
            port=port,
            use_iam_auth=use_iam_auth,
            region=region,
            namespace=self.namespace
        )
        
        # Initialize Neptune vector store
        self.vector_store = NeptuneVectorStore(
            endpoint=endpoint,
            port=port,
            use_iam_auth=use_iam_auth,
            region=region,
            namespace=self.namespace
        )
