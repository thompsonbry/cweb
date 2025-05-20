#!/usr/bin/env python3
"""
Query a lexical graph using GraphRAG Toolkit.
"""

import os
import sys
import argparse
import logging
import json
from typing import List, Dict, Any
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

def query_lexical_graph(query: str, top_k: int = 10, verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Query a lexical graph.
    
    Args:
        query (str): The query string
        top_k (int, optional): The number of results to return
        verbose (bool, optional): Enable verbose output
        
    Returns:
        List[Dict[str, Any]]: The query results
    """
    try:
        from src.graphrag_integration.lexical_graph_builder import LexicalGraphBuilder
        
        # Set log level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Query lexical graph
        logger.info(f"Querying lexical graph with: {query}")
        graph_builder = LexicalGraphBuilder()
        results = graph_builder.query_graph(query, top_k=top_k)
        
        logger.info(f"Found {len(results)} results")
        return results
    
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        logger.error("Make sure GraphRAG Toolkit is properly linked in the lib directory.")
        return []
    
    except Exception as e:
        logger.error(f"Error querying lexical graph: {str(e)}")
        if verbose:
            import traceback
            logger.error(traceback.format_exc())
        return []

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Query a lexical graph")
    parser.add_argument("query", help="The query string")
    parser.add_argument("--top-k", type=int, default=10, help="The number of results to return")
    parser.add_argument("--output", "-o", help="Output file path (JSON format)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    results = query_lexical_graph(args.query, args.top_k, args.verbose)
    
    if not results:
        logger.error("No results found or an error occurred")
        sys.exit(1)
    
    # Print results
    print(json.dumps(results, indent=2))
    
    # Save results to file if specified
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {args.output}")
        except Exception as e:
            logger.error(f"Error saving results to file: {str(e)}")
            sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
