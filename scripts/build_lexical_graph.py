#!/usr/bin/env python3
"""
Build a lexical graph from a text file using GraphRAG Toolkit and Neptune Analytics.
"""

import os
import sys
import argparse
import logging
import boto3
from typing import Optional
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Add the GraphRAG lexical-graph to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib/graphrag-lexical-graph/src'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_neptune_analytics_client():
    """
    Get a Neptune Analytics client.
    
    Returns:
        boto3.client: The Neptune Analytics client
    """
    region = os.environ.get("NEPTUNE_ANALYTICS_REGION", "us-west-2")
    return boto3.client("neptune-graph", region_name=region)

def get_bedrock_client():
    """
    Get a Bedrock client.
    
    Returns:
        boto3.client: The Bedrock client
    """
    region = os.environ.get("AWS_REGION", "us-east-1")
    return boto3.client("bedrock-runtime", region_name=region)

def build_lexical_graph(file_path: str, document_id: Optional[str] = None, verbose: bool = False) -> bool:
    """
    Build a lexical graph from a text file.
    
    Args:
        file_path (str): Path to the text file
        document_id (str, optional): The document ID (defaults to file name)
        verbose (bool, optional): Enable verbose output
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Import GraphRAG components
        try:
            from graphrag_toolkit.lexical_graph.document.document import Document
            from graphrag_toolkit.lexical_graph.document.document_processor import DocumentProcessor
            from graphrag_toolkit.lexical_graph.fact.fact_extractor import FactExtractor
            from graphrag_toolkit.lexical_graph.graph.graph import Graph
            from graphrag_toolkit.lexical_graph.graph.vector_store import VectorStore
            from graphrag_toolkit.lexical_graph.graph.lexical_graph import LexicalGraph
            from graphrag_toolkit.lexical_graph.embedding.bedrock_embedding_model import BedrockEmbeddingModel
            from graphrag_toolkit.lexical_graph.llm.bedrock_llm import BedrockLLM
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            logger.error("Make sure GraphRAG Toolkit is properly linked in the lib directory.")
            return False
        
        # Set log level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Use file name as document ID if not provided
        if document_id is None:
            document_id = os.path.basename(file_path)
        
        # Create document
        logger.info(f"Creating document from {file_path}...")
        document = Document(
            id=document_id,
            text=text,
            metadata={"source_file": file_path}
        )
        
        # Initialize Bedrock embedding model
        logger.info("Initializing Bedrock embedding model...")
        bedrock_client = get_bedrock_client()
        embedding_model = BedrockEmbeddingModel(
            client=bedrock_client,
            model_id="amazon.titan-embed-text-v1"
        )
        
        # Process document
        logger.info("Processing document...")
        document_processor = DocumentProcessor(
            embedding_model=embedding_model,
            chunk_size=512,
            chunk_overlap=128,
            max_tokens_per_chunk=512
        )
        processed_document = document_processor.process(document)
        
        # Initialize Bedrock LLM
        logger.info("Initializing Bedrock LLM...")
        llm = BedrockLLM(
            client=bedrock_client,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        # Extract facts
        logger.info("Extracting facts...")
        fact_extractor = FactExtractor(
            llm=llm,
            namespace="cweb"
        )
        facts = fact_extractor.extract_facts(processed_document)
        
        logger.info(f"Extracted {len(facts)} facts from document {document.id}")
        
        if verbose and facts:
            logger.debug("Sample facts:")
            for i, fact in enumerate(facts[:5]):
                logger.debug(f"Fact {i+1}: {fact.subject} {fact.predicate} {fact.object}")
        
        # Initialize Neptune Analytics graph
        logger.info("Initializing Neptune Analytics graph...")
        
        # Create custom Neptune Analytics Graph implementation
        from src.graphrag_integration.neptune_analytics_adapter import NeptuneAnalyticsGraph, NeptuneAnalyticsVectorStore
        
        # Get Neptune Analytics connection info
        region = os.environ.get("NEPTUNE_ANALYTICS_REGION", "us-west-2")
        graph_id = os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID", "g-k2n0lshd74")
        use_iam_auth = True
        namespace = "cweb"
        
        # Initialize Neptune Analytics graph and vector store
        graph = NeptuneAnalyticsGraph(
            region=region,
            graph_id=graph_id,
            use_iam_auth=use_iam_auth,
            namespace=namespace
        )
        
        vector_store = NeptuneAnalyticsVectorStore(
            region=region,
            graph_id=graph_id,
            use_iam_auth=use_iam_auth,
            namespace=namespace
        )
        
        # Build lexical graph
        logger.info("Building lexical graph...")
        lexical_graph = LexicalGraph(
            graph=graph,
            vector_store=vector_store,
            namespace=namespace
        )
        
        # Add document and facts to lexical graph
        lexical_graph.add_document(processed_document)
        lexical_graph.add_facts(facts)
        
        logger.info("Lexical graph built successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error building lexical graph: {str(e)}")
        if verbose:
            import traceback
            logger.error(traceback.format_exc())
        return False

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Build a lexical graph from a text file")
    parser.add_argument("file_path", help="Path to the text file")
    parser.add_argument("--document-id", help="Document ID (defaults to file name)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        logger.error(f"File not found: {args.file_path}")
        sys.exit(1)
    
    if build_lexical_graph(args.file_path, args.document_id, args.verbose):
        logger.info("Lexical graph built successfully")
        sys.exit(0)
    else:
        logger.error("Failed to build lexical graph")
        sys.exit(1)

if __name__ == "__main__":
    main()
