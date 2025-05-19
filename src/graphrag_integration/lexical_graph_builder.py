"""
Lexical graph builder for GraphRAG Toolkit integration.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional, Tuple

# Add the GraphRAG lexical-graph to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lib/graphrag-lexical-graph/src'))

# Import GraphRAG components
try:
    from graphrag_toolkit.lexical_graph.document.document import Document
    from graphrag_toolkit.lexical_graph.fact.fact import Fact
    from graphrag_toolkit.lexical_graph.graph.lexical_graph import LexicalGraph
except ImportError:
    raise ImportError(
        "Failed to import GraphRAG Toolkit. Make sure the lexical-graph module "
        "is properly linked in the lib directory."
    )

from src.graphrag_integration.config import GRAPHRAG_CONFIG
from src.graphrag_integration.neptune_analytics_adapter import NeptuneAnalyticsAdapter

logger = logging.getLogger(__name__)

class LexicalGraphBuilder:
    """
    Lexical graph builder for CWEB project using GraphRAG Toolkit.
    """
    
    def __init__(self):
        """
        Initialize the lexical graph builder.
        """
        self.config = GRAPHRAG_CONFIG
        self.namespace = self.config["lexical_graph"]["namespace"]
        self.neptune_adapter = NeptuneAnalyticsAdapter()
        
        # Initialize lexical graph
        self.lexical_graph = LexicalGraph(
            graph=self.neptune_adapter.graph,
            vector_store=self.neptune_adapter.vector_store,
            namespace=self.namespace
        )
    
    def add_document(self, document: Document) -> None:
        """
        Add a document to the lexical graph.
        
        Args:
            document (Document): The document to add
        """
        self.lexical_graph.add_document(document)
    
    def add_facts(self, facts: List[Fact]) -> None:
        """
        Add facts to the lexical graph.
        
        Args:
            facts (List[Fact]): The facts to add
        """
        self.lexical_graph.add_facts(facts)
    
    def add_document_and_facts(self, document: Document, facts: List[Fact]) -> None:
        """
        Add a document and its facts to the lexical graph.
        
        Args:
            document (Document): The document to add
            facts (List[Fact]): The facts to add
        """
        # Add document
        self.add_document(document)
        
        # Add facts
        self.add_facts(facts)
    
    def query_graph(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Query the lexical graph.
        
        Args:
            query (str): The query string
            top_k (int, optional): The number of results to return
            
        Returns:
            List[Dict[str, Any]]: The query results
        """
        return self.lexical_graph.query(query, top_k=top_k)
    
    def get_facts_by_document_id(self, document_id: str) -> List[Fact]:
        """
        Get facts by document ID.
        
        Args:
            document_id (str): The document ID
            
        Returns:
            List[Fact]: The facts
        """
        return self.lexical_graph.get_facts_by_document_id(document_id)
