#!/usr/bin/env python3
"""
Build a lexical graph from a text file using GraphRAG Toolkit.
"""

import os
import sys
import argparse
import logging
from typing import Optional
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        from src.graphrag_integration.fact_extractor import CwebFactExtractor
        from src.graphrag_integration.lexical_graph_builder import LexicalGraphBuilder
        
        # Set log level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Extract facts from file
        logger.info(f"Extracting facts from {file_path}...")
        fact_extractor = CwebFactExtractor()
        document, facts = fact_extractor.extract_facts_from_file(file_path, document_id)
        
        logger.info(f"Extracted {len(facts)} facts from document {document.id}")
        
        if verbose:
            logger.debug("Sample facts:")
            for i, fact in enumerate(facts[:5]):
                logger.debug(f"Fact {i+1}: {fact}")
        
        # Build lexical graph
        logger.info("Building lexical graph...")
        graph_builder = LexicalGraphBuilder()
        graph_builder.add_document_and_facts(document, facts)
        
        logger.info("Lexical graph built successfully")
        return True
    
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        logger.error("Make sure GraphRAG Toolkit is properly linked in the lib directory.")
        return False
    
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
