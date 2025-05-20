#!/usr/bin/env python3
"""
Update Neptune configuration in project files.
"""

import os
import sys
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

def update_config_files(verbose=False):
    """
    Update Neptune configuration in project files.
    
    Args:
        verbose (bool, optional): Enable verbose output
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get Neptune Analytics endpoint
        logger.info("Getting Neptune Analytics endpoint...")
        target_endpoint = get_neptune_analytics_endpoint()
        
        logger.info(f"Neptune Analytics endpoint: {target_endpoint}")
        
        # Update .env file if it exists
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_file):
            logger.info(f"Updating {env_file}...")
            
            with open(env_file, "r") as f:
                lines = f.readlines()
            
            updated = False
            with open(env_file, "w") as f:
                for line in lines:
                    if line.startswith("NEPTUNE_ENDPOINT="):
                        f.write(f"NEPTUNE_ENDPOINT={target_endpoint}\n")
                        updated = True
                    else:
                        f.write(line)
                
                if not updated:
                    f.write(f"NEPTUNE_ENDPOINT={target_endpoint}\n")
            
            logger.info(f"Updated {env_file}")
        else:
            logger.info(f"{env_file} does not exist, creating...")
            
            with open(env_file, "w") as f:
                f.write(f"NEPTUNE_ENDPOINT={target_endpoint}\n")
            
            logger.info(f"Created {env_file}")
        
        # Update config.py if it exists
        config_file = os.path.join(os.path.dirname(__file__), "..", "src", "config.py")
        if os.path.exists(config_file):
            logger.info(f"Updating {config_file}...")
            
            with open(config_file, "r") as f:
                lines = f.readlines()
            
            updated = False
            with open(config_file, "w") as f:
                for line in lines:
                    if "NEPTUNE_ENDPOINT" in line and "=" in line:
                        f.write(f'NEPTUNE_ENDPOINT = "{target_endpoint}"\n')
                        updated = True
                    else:
                        f.write(line)
                
                if not updated:
                    f.write('\n# Neptune Analytics configuration\n')
                    f.write(f'NEPTUNE_ENDPOINT = "{target_endpoint}"\n')
            
            logger.info(f"Updated {config_file}")
        
        # Update config.json if it exists
        config_json = os.path.join(os.path.dirname(__file__), "..", "config.json")
        if os.path.exists(config_json):
            logger.info(f"Updating {config_json}...")
            
            import json
            with open(config_json, "r") as f:
                config = json.load(f)
            
            config["neptune_endpoint"] = target_endpoint
            
            with open(config_json, "w") as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Updated {config_json}")
        
        logger.info("Neptune configuration updated successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error updating Neptune configuration: {str(e)}")
        if verbose:
            import traceback
            logger.error(traceback.format_exc())
        return False

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Update Neptune configuration in project files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if update_config_files(args.verbose):
        logger.info("Configuration updated successfully")
        sys.exit(0)
    else:
        logger.error("Failed to update configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()
