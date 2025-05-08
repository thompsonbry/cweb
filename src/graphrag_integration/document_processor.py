"""
Document processor for GraphRAG Toolkit integration.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional

# Add the GraphRAG lexical-graph to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lib/graphrag-lexical-graph/src'))

# Import GraphRAG components
try:
    from graphrag.toolkit.lexical_graph.document.document_processor import DocumentProcessor
    from graphrag.toolkit.lexical_graph.document.document import Document
    from graphrag.toolkit.lexical_graph.document.chunk import Chunk
    from graphrag.toolkit.lexical_graph.embedding.bedrock_embedding import BedrockEmbedding
except ImportError:
    raise ImportError(
        "Failed to import GraphRAG Toolkit. Make sure the lexical-graph module "
        "is properly linked in the lib directory."
    )

from src.graphrag_integration.config import GRAPHRAG_CONFIG, get_bedrock_client

logger = logging.getLogger(__name__)

class CwebDocumentProcessor:
    """
    Document processor for CWEB project using GraphRAG Toolkit.
    """
    
    def __init__(self):
        """
        Initialize the document processor.
        """
        self.config = GRAPHRAG_CONFIG
        self.bedrock_client = get_bedrock_client()
        
        # Initialize embedding model
        self.embedding_model = BedrockEmbedding(
            client=self.bedrock_client,
            model_id=self.config["bedrock"]["embedding_model"]
        )
        
        # Initialize document processor
        self.processor = DocumentProcessor(
            embedding_model=self.embedding_model,
            chunk_size=self.config["lexical_graph"]["chunk_size"],
            chunk_overlap=self.config["lexical_graph"]["chunk_overlap"],
            max_tokens_per_chunk=self.config["lexical_graph"]["max_tokens_per_chunk"]
        )
    
    def process_text(self, text: str, document_id: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """
        Process text and create a Document object.
        
        Args:
            text (str): The text to process
            document_id (str): The document ID
            metadata (Dict[str, Any], optional): Document metadata
            
        Returns:
            Document: The processed document
        """
        if metadata is None:
            metadata = {}
        
        # Create document
        document = Document(
            id=document_id,
            text=text,
            metadata=metadata
        )
        
        # Process document (chunk and embed)
        processed_document = self.processor.process(document)
        
        return processed_document
    
    def process_file(self, file_path: str, document_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """
        Process a text file and create a Document object.
        
        Args:
            file_path (str): Path to the text file
            document_id (str, optional): The document ID (defaults to file name)
            metadata (Dict[str, Any], optional): Document metadata
            
        Returns:
            Document: The processed document
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Use file name as document ID if not provided
        if document_id is None:
            document_id = os.path.basename(file_path)
        
        # Add file path to metadata
        if metadata is None:
            metadata = {}
        metadata['source_file'] = file_path
        
        # Process text
        return self.process_text(text, document_id, metadata)
