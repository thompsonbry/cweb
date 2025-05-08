"""
Neptune Analytics adapter for GraphRAG Toolkit.
"""

import sys
import os
import boto3
from src.graphrag_integration.config import get_neptune_connection_info, GRAPHRAG_CONFIG

# Add the GraphRAG lexical-graph to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lib/graphrag-lexical-graph/src'))

# Import GraphRAG components
try:
    from graphrag.toolkit.lexical_graph.graph.neptune_graph import NeptuneGraph
    from graphrag.toolkit.lexical_graph.graph.neptune_vector_store import NeptuneVectorStore
except ImportError:
    raise ImportError(
        "Failed to import GraphRAG Toolkit. Make sure the lexical-graph module "
        "is properly linked in the lib directory."
    )

class NeptuneAdapter:
    """
    Adapter class for integrating GraphRAG Toolkit with Neptune Analytics.
    """
    
    def __init__(self):
        """
        Initialize the Neptune adapter with connection information.
        """
        self.connection_info = get_neptune_connection_info()
        self.namespace = GRAPHRAG_CONFIG["lexical_graph"]["namespace"]
        self.vector_dimension = GRAPHRAG_CONFIG["neptune"]["vector_dimension"]
        self.region = GRAPHRAG_CONFIG["neptune"]["region"]
        
        # Initialize Neptune graph and vector store
        self._graph = None
        self._vector_store = None
    
    @property
    def graph(self):
        """
        Get or create the Neptune graph instance.
        """
        if self._graph is None:
            self._graph = NeptuneGraph(
                endpoint=self.connection_info["endpoint"],
                port=self.connection_info["port"],
                auth_mode=self.connection_info["auth_mode"],
                region=self.region,
                namespace=self.namespace
            )
        return self._graph
    
    @property
    def vector_store(self):
        """
        Get or create the Neptune vector store instance.
        """
        if self._vector_store is None:
            self._vector_store = NeptuneVectorStore(
                endpoint=self.connection_info["endpoint"],
                port=self.connection_info["port"],
                auth_mode=self.connection_info["auth_mode"],
                region=self.region,
                namespace=self.namespace,
                dimension=self.vector_dimension
            )
        return self._vector_store
    
    def initialize_schema(self):
        """
        Initialize the GraphRAG schema in Neptune Analytics.
        """
        # This method would create the necessary property graph schema
        # for the GraphRAG lexical graph in Neptune Analytics
        pass
    
    def test_connection(self):
        """
        Test the connection to Neptune Analytics.
        """
        try:
            # Test graph connection
            status = self.graph.test_connection()
            print(f"Graph connection test: {status}")
            
            # Test vector store connection
            status = self.vector_store.test_connection()
            print(f"Vector store connection test: {status}")
            
            return True
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False
