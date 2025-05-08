"""
Fact extractor for GraphRAG Toolkit integration.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional, Tuple

# Add the GraphRAG lexical-graph to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lib/graphrag-lexical-graph/src'))

# Import GraphRAG components
try:
    from graphrag.toolkit.lexical_graph.document.document import Document
    from graphrag.toolkit.lexical_graph.document.chunk import Chunk
    from graphrag.toolkit.lexical_graph.fact.fact_extractor import FactExtractor
    from graphrag.toolkit.lexical_graph.fact.fact import Fact
    from graphrag.toolkit.lexical_graph.llm.bedrock_llm import BedrockLLM
except ImportError:
    raise ImportError(
        "Failed to import GraphRAG Toolkit. Make sure the lexical-graph module "
        "is properly linked in the lib directory."
    )

from src.graphrag_integration.config import GRAPHRAG_CONFIG, get_bedrock_client

logger = logging.getLogger(__name__)

class CwebFactExtractor:
    """
    Fact extractor for CWEB project using GraphRAG Toolkit.
    """
    
    def __init__(self):
        """
        Initialize the fact extractor.
        """
        self.config = GRAPHRAG_CONFIG
        self.bedrock_client = get_bedrock_client()
        
        # Initialize LLM
        self.llm = BedrockLLM(
            client=self.bedrock_client,
            model_id=self.config["bedrock"]["llm_model"]
        )
        
        # Initialize fact extractor
        self.extractor = FactExtractor(
            llm=self.llm,
            namespace=self.config["lexical_graph"]["namespace"]
        )
    
    def extract_facts(self, document: Document) -> List[Fact]:
        """
        Extract facts from a document.
        
        Args:
            document (Document): The document to extract facts from
            
        Returns:
            List[Fact]: The extracted facts
        """
        # Extract facts from document
        facts = self.extractor.extract_facts(document)
        
        return facts
    
    def extract_facts_from_text(self, text: str, document_id: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[Document, List[Fact]]:
        """
        Extract facts from text.
        
        Args:
            text (str): The text to extract facts from
            document_id (str): The document ID
            metadata (Dict[str, Any], optional): Document metadata
            
        Returns:
            Tuple[Document, List[Fact]]: The processed document and extracted facts
        """
        from src.graphrag_integration.document_processor import CwebDocumentProcessor
        
        # Process text
        processor = CwebDocumentProcessor()
        document = processor.process_text(text, document_id, metadata)
        
        # Extract facts
        facts = self.extract_facts(document)
        
        return document, facts
    
    def extract_facts_from_file(self, file_path: str, document_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Tuple[Document, List[Fact]]:
        """
        Extract facts from a text file.
        
        Args:
            file_path (str): Path to the text file
            document_id (str, optional): The document ID (defaults to file name)
            metadata (Dict[str, Any], optional): Document metadata
            
        Returns:
            Tuple[Document, List[Fact]]: The processed document and extracted facts
        """
        from src.graphrag_integration.document_processor import CwebDocumentProcessor
        
        # Process file
        processor = CwebDocumentProcessor()
        document = processor.process_file(file_path, document_id, metadata)
        
        # Extract facts
        facts = self.extract_facts(document)
        
        return document, facts
