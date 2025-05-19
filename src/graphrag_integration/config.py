#!/usr/bin/env python3

"""
Configuration module for GraphRAG integration.

This module provides configuration utilities for the GraphRAG toolkit
integration with Neptune Analytics.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class GraphRAGConfig:
    """Configuration for GraphRAG toolkit."""
    
    # Default values
    DEFAULT_AWS_REGION = "us-west-2"
    DEFAULT_EMBED_MODEL = "cohere.embed-english-v3"
    DEFAULT_EMBED_DIMENSIONS = 1024
    DEFAULT_EXTRACTION_LLM = "anthropic.claude-3-sonnet-20240229-v1:0"
    DEFAULT_RESPONSE_LLM = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    @staticmethod
    def get_neptune_analytics_config() -> Dict[str, str]:
        """
        Get Neptune Analytics configuration from environment variables.
        
        Returns:
            Dict[str, str]: Neptune Analytics configuration
        """
        graph_id = os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID")
        region = os.environ.get("NEPTUNE_ANALYTICS_REGION", GraphRAGConfig.DEFAULT_AWS_REGION)
        
        if not graph_id:
            logger.warning("NEPTUNE_ANALYTICS_GRAPH_ID not found in environment variables")
        
        return {
            "graph_id": graph_id,
            "region": region,
            "connection_string": f"neptune-graph://{graph_id}" if graph_id else None
        }
    
    @staticmethod
    def get_bedrock_config() -> Dict[str, str]:
        """
        Get Amazon Bedrock configuration from environment variables.
        
        Returns:
            Dict[str, str]: Bedrock configuration
        """
        region = os.environ.get("BEDROCK_REGION", GraphRAGConfig.DEFAULT_AWS_REGION)
        
        return {
            "region": region,
            "embed_model": GraphRAGConfig.DEFAULT_EMBED_MODEL,
            "embed_dimensions": GraphRAGConfig.DEFAULT_EMBED_DIMENSIONS,
            "extraction_llm": GraphRAGConfig.DEFAULT_EXTRACTION_LLM,
            "response_llm": GraphRAGConfig.DEFAULT_RESPONSE_LLM
        }
    
    @staticmethod
    def configure_graphrag_toolkit() -> bool:
        """
        Configure GraphRAG toolkit with settings from environment variables.
        
        Returns:
            bool: True if configuration was successful, False otherwise
        """
        try:
            from graphrag_toolkit.lexical_graph import GraphRAGConfig as ToolkitConfig
            from graphrag_toolkit.lexical_graph import set_logging_config
            
            # Get configurations
            neptune_config = GraphRAGConfig.get_neptune_analytics_config()
            bedrock_config = GraphRAGConfig.get_bedrock_config()
            
            # Configure GraphRAG toolkit
            ToolkitConfig.aws_region = neptune_config["region"]
            ToolkitConfig.embed_model = bedrock_config["embed_model"]
            ToolkitConfig.embed_dimensions = bedrock_config["embed_dimensions"]
            ToolkitConfig.extraction_llm = bedrock_config["extraction_llm"]
            ToolkitConfig.response_llm = bedrock_config["response_llm"]
            
            # Set logging
            set_logging_config('INFO')
            
            logger.info(f"Configured GraphRAG toolkit with:")
            logger.info(f"  AWS Region: {ToolkitConfig.aws_region}")
            logger.info(f"  Embed Model: {ToolkitConfig.embed_model}")
            logger.info(f"  Embed Dimensions: {ToolkitConfig.embed_dimensions}")
            logger.info(f"  Extraction LLM: {ToolkitConfig.extraction_llm}")
            logger.info(f"  Response LLM: {ToolkitConfig.response_llm}")
            
            return True
        except ImportError as e:
            logger.error(f"Failed to configure GraphRAG toolkit: {e}")
            return False
        except Exception as e:
            logger.error(f"Error configuring GraphRAG toolkit: {e}")
            return False
