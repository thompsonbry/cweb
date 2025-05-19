#!/usr/bin/env python3

"""
Neptune Analytics Adapter for GraphRAG

This module provides adapter classes and utilities for integrating
Neptune Analytics with the GraphRAG toolkit.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

class NeptuneAnalyticsAdapter:
    """
    Adapter class for Neptune Analytics integration with GraphRAG toolkit.
    
    This class provides methods for connecting to Neptune Analytics,
    executing queries, and managing graph data.
    """
    
    def __init__(self, graph_id: str = None, region: str = None):
        """
        Initialize the Neptune Analytics adapter.
        
        Args:
            graph_id: Neptune Analytics graph ID
            region: AWS region for Neptune Analytics
        """
        self.graph_id = graph_id or os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID")
        self.region = region or os.environ.get("NEPTUNE_ANALYTICS_REGION", "us-west-2")
        
        if not self.graph_id:
            raise ValueError("Neptune Analytics graph ID not provided and not found in environment variables")
        
        # Connection string for Neptune Analytics
        self.connection_string = f"neptune-graph://{self.graph_id}"
        logger.info(f"Initialized Neptune Analytics adapter for graph {self.graph_id} in {self.region}")
    
    def get_connection_string(self) -> str:
        """
        Get the Neptune Analytics connection string.
        
        Returns:
            str: Connection string for Neptune Analytics
        """
        return self.connection_string
    
    def get_graph_store_config(self) -> Dict[str, Any]:
        """
        Get configuration for GraphRAG graph store.
        
        Returns:
            Dict[str, Any]: Configuration dictionary for graph store
        """
        return {
            "connection_string": self.connection_string,
            "region": self.region
        }
    
    def get_vector_store_config(self) -> Dict[str, Any]:
        """
        Get configuration for GraphRAG vector store.
        
        Returns:
            Dict[str, Any]: Configuration dictionary for vector store
        """
        return {
            "connection_string": self.connection_string,
            "region": self.region
        }
    
    @staticmethod
    def configure_graphrag(embed_model: str = "cohere.embed-english-v3", 
                          embed_dimensions: int = 1024,
                          extraction_llm: str = "anthropic.claude-3-sonnet-20240229-v1:0",
                          response_llm: str = "anthropic.claude-3-sonnet-20240229-v1:0",
                          aws_region: str = None):
        """
        Configure GraphRAG toolkit for Neptune Analytics.
        
        Args:
            embed_model: Embedding model to use
            embed_dimensions: Embedding dimensions
            extraction_llm: LLM for extraction
            response_llm: LLM for responses
            aws_region: AWS region
        """
        try:
            from graphrag_toolkit.lexical_graph import GraphRAGConfig, set_logging_config
            
            # Set AWS region
            GraphRAGConfig.aws_region = aws_region or os.environ.get("AWS_REGION", "us-west-2")
            
            # Configure embedding model
            GraphRAGConfig.embed_model = embed_model
            GraphRAGConfig.embed_dimensions = embed_dimensions
            
            # Configure LLMs
            GraphRAGConfig.extraction_llm = extraction_llm
            GraphRAGConfig.response_llm = response_llm
            
            # Set logging
            set_logging_config('INFO')
            
            logger.info(f"Configured GraphRAG with embedding model {embed_model} ({embed_dimensions} dimensions)")
            logger.info(f"Using extraction LLM: {extraction_llm}")
            logger.info(f"Using response LLM: {response_llm}")
            logger.info(f"AWS region: {GraphRAGConfig.aws_region}")
            
            return True
        except ImportError as e:
            logger.error(f"Failed to configure GraphRAG: {e}")
            return False
    
    @staticmethod
    def initialize_graph_stores(connection_string: str = None, graph_id: str = None, region: str = None):
        """
        Initialize graph and vector stores for Neptune Analytics.
        
        Args:
            connection_string: Neptune Analytics connection string
            graph_id: Neptune Analytics graph ID
            region: AWS region
        
        Returns:
            tuple: (graph_store, vector_store)
        """
        try:
            from graphrag_toolkit.lexical_graph.storage import GraphStoreFactory, VectorStoreFactory
            
            # Build connection string if not provided
            if not connection_string and graph_id:
                connection_string = f"neptune-graph://{graph_id}"
            
            if not connection_string:
                adapter = NeptuneAnalyticsAdapter(graph_id, region)
                connection_string = adapter.get_connection_string()
            
            # Create stores
            graph_store = GraphStoreFactory.for_graph_store(connection_string)
            vector_store = VectorStoreFactory.for_vector_store(connection_string)
            
            logger.info(f"Initialized graph and vector stores for {connection_string}")
            
            return graph_store, vector_store
        except Exception as e:
            logger.error(f"Failed to initialize graph stores: {e}")
            raise
