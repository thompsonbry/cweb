#!/usr/bin/env python3
"""
Query a lexical graph using mock GraphRAG Toolkit implementation.
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

def load_mock_graph():
    """
    Load a mock graph with facts from the WCNN 1995 paper.
    """
    from src.graphrag_integration.mock_implementation import Document, LexicalGraph, Fact
    
    # Create a mock graph
    graph = LexicalGraph(namespace="cweb")
    
    # Add document
    document = Document(
        id="wcnn_1995",
        text="WCNN 1995 Paper Summary",
        metadata={"source_file": "test/data/wcnn_1995_text.txt"}
    )
    graph.add_document(document)
    
    # Add facts
    facts = [
        Fact(
            id="wcnn_1995_fact_1",
            subject="Recognition/Metacognition Framework",
            predicate="is",
            object="model of tactical decision making"
        ),
        Fact(
            id="wcnn_1995_fact_2",
            subject="Recognition/Metacognition Framework",
            predicate="integrates",
            object="recognition-primed decision making with metacognitive processes"
        ),
        Fact(
            id="wcnn_1995_fact_3",
            subject="Recognition-Primed Decision Making",
            predicate="includes",
            object="pattern matching to recognize situations"
        ),
        Fact(
            id="wcnn_1995_fact_4",
            subject="Recognition-Primed Decision Making",
            predicate="includes",
            object="mental simulation to evaluate courses of action"
        ),
        Fact(
            id="wcnn_1995_fact_5",
            subject="Metacognitive Processes",
            predicate="include",
            object="Quick Test"
        ),
        Fact(
            id="wcnn_1995_fact_6",
            subject="Metacognitive Processes",
            predicate="include",
            object="Story Building"
        ),
        Fact(
            id="wcnn_1995_fact_7",
            subject="Metacognitive Processes",
            predicate="include",
            object="Assumption Testing"
        ),
        Fact(
            id="wcnn_1995_fact_8",
            subject="Metacognitive Processes",
            predicate="include",
            object="Attention Management"
        ),
        Fact(
            id="wcnn_1995_fact_9",
            subject="Critical Thinking Strategies",
            predicate="include",
            object="identifying evidence-conclusion relationships"
        ),
        Fact(
            id="wcnn_1995_fact_10",
            subject="Critical Thinking Strategies",
            predicate="include",
            object="detecting inconsistencies in situation assessment"
        ),
        Fact(
            id="wcnn_1995_fact_11",
            subject="R/M Framework",
            predicate="has been applied to",
            object="military command and control"
        ),
        Fact(
            id="wcnn_1995_fact_12",
            subject="R/M Framework",
            predicate="has been applied to",
            object="emergency management"
        ),
        Fact(
            id="wcnn_1995_fact_13",
            subject="R/M Framework",
            predicate="has been applied to",
            object="intelligence analysis"
        ),
        Fact(
            id="wcnn_1995_fact_14",
            subject="R/M Framework",
            predicate="provides",
            object="comprehensive model of tactical decision making"
        ),
    ]
    graph.add_facts(facts)
    
    return graph

def query_lexical_graph(query: str, top_k: int = 10, verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Query a lexical graph using mock implementation.
    
    Args:
        query (str): The query string
        top_k (int, optional): The number of results to return
        verbose (bool, optional): Enable verbose output
        
    Returns:
        List[Dict[str, Any]]: The query results
    """
    try:
        # Set log level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Load mock graph
        logger.info("Loading mock graph...")
        graph = load_mock_graph()
        
        # Query lexical graph
        logger.info(f"Querying lexical graph with: {query}")
        results = graph.query(query, top_k=top_k)
        
        logger.info(f"Found {len(results)} results")
        return results
    
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
