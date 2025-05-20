#!/usr/bin/env python3
"""
Create a metacognitive schema in Neptune Analytics using OpenCypher.
"""

import os
import sys
import boto3
import argparse
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_neptune_analytics_endpoint():
    """
    Get the Neptune Analytics endpoint from the graph ID.
    
    Returns:
        str: The Neptune Analytics endpoint
    """
    graph_id = os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID")
    if not graph_id:
        raise ValueError("NEPTUNE_ANALYTICS_GRAPH_ID environment variable is required")
    
    region = os.environ.get("NEPTUNE_ANALYTICS_REGION", "us-west-2")
    return f"{graph_id}.{region}.neptune-graph.amazonaws.com"

def get_neptune_analytics_client():
    """
    Get a Neptune Analytics client.
    
    Returns:
        boto3.client: The Neptune Analytics client
    """
    region = os.environ.get("NEPTUNE_ANALYTICS_REGION", "us-west-2")
    return boto3.client("neptune-graph", region_name=region)

def execute_query(client, graph_id, query):
    """
    Execute an OpenCypher query against Neptune Analytics.
    
    Args:
        client (boto3.client): The Neptune Analytics client
        graph_id (str): The graph ID
        query (str): The OpenCypher query
        
    Returns:
        list: The query results
    """
    response = client.execute_query(
        graphIdentifier=graph_id,
        language="OPEN_CYPHER",
        queryString=query
    )
    
    results = []
    for record in response.get("results", []):
        result_dict = {}
        for key, value in record.items():
            # Convert Neptune Analytics value format to Python native types
            if "stringValue" in value:
                result_dict[key] = value["stringValue"]
            elif "integerValue" in value:
                result_dict[key] = int(value["integerValue"])
            elif "doubleValue" in value:
                result_dict[key] = float(value["doubleValue"])
            elif "booleanValue" in value:
                result_dict[key] = value["booleanValue"]
            elif "listValue" in value:
                result_dict[key] = value["listValue"]
            elif "mapValue" in value:
                result_dict[key] = value["mapValue"]
            else:
                result_dict[key] = str(value)
        results.append(result_dict)
    
    return results

def create_metacog_schema(verbose=False):
    """
    Create a metacognitive schema in Neptune Analytics.
    
    Args:
        verbose (bool, optional): Enable verbose output
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get Neptune Analytics client
        logger.info("Initializing Neptune Analytics client...")
        client = get_neptune_analytics_client()
        
        # Get Neptune Analytics endpoint
        logger.info("Getting Neptune Analytics endpoint...")
        graph_endpoint = get_neptune_analytics_endpoint()
        
        # Get graph ID
        graph_id = os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID")
        if not graph_id:
            raise ValueError("NEPTUNE_ANALYTICS_GRAPH_ID environment variable is required")
        
        logger.info(f"Neptune Analytics endpoint: {graph_endpoint}")
        
        # Create metacognitive schema
        logger.info("Creating metacognitive schema...")
        
        # Create Concept node
        concept_query = """
        CREATE (c:Concept {
            id: 'concept-1',
            name: 'Metacognition',
            description: 'Awareness and understanding of one\'s own thought processes'
        })
        RETURN c
        """
        
        execute_query(client, graph_id, concept_query)
        logger.info("Created Concept node")
        
        # Create Argument node
        argument_query = """
        CREATE (a:Argument {
            id: 'argument-1',
            name: 'Metacognition Improves Learning',
            description: 'The argument that metacognitive strategies improve learning outcomes'
        })
        RETURN a
        """
        
        execute_query(client, graph_id, argument_query)
        logger.info("Created Argument node")
        
        # Create Evidence node
        evidence_query = """
        CREATE (e:Evidence {
            id: 'evidence-1',
            name: 'Study Results',
            description: 'Results from studies showing improved learning outcomes with metacognitive strategies'
        })
        RETURN e
        """
        
        execute_query(client, graph_id, evidence_query)
        logger.info("Created Evidence node")
        
        # Create relationships
        relationship_query = """
        MATCH (a:Argument {id: 'argument-1'})
        MATCH (c:Concept {id: 'concept-1'})
        MATCH (e:Evidence {id: 'evidence-1'})
        CREATE (a)-[:RELATES_TO]->(c)
        CREATE (e)-[:SUPPORTS]->(a)
        RETURN a, c, e
        """
        
        execute_query(client, graph_id, relationship_query)
        logger.info("Created relationships")
        
        logger.info("Metacognitive schema created successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error creating metacognitive schema: {str(e)}")
        if verbose:
            import traceback
            logger.error(traceback.format_exc())
        return False

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Create a metacognitive schema in Neptune Analytics")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if create_metacog_schema(args.verbose):
        logger.info("Schema created successfully")
        sys.exit(0)
    else:
        logger.error("Failed to create schema")
        sys.exit(1)

if __name__ == "__main__":
    main()
