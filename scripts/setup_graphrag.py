#!/usr/bin/env python3
"""
Setup script for GraphRAG Toolkit integration with Neptune Analytics.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

def setup_graphrag():
    """
    Setup GraphRAG Toolkit integration with Neptune Analytics.
    """
    try:
        from src.graphrag_integration.neptune_adapter import NeptuneAdapter
        
        print("Initializing Neptune adapter for GraphRAG...")
        adapter = NeptuneAdapter()
        
        print("Testing connection to Neptune Analytics...")
        if adapter.test_connection():
            print("Connection successful!")
        else:
            print("Connection failed. Please check your Neptune configuration.")
            return False
        
        print("Setting up GraphRAG schema in Neptune Analytics...")
        adapter.initialize_schema()
        
        print("GraphRAG Toolkit integration setup complete!")
        return True
    except ImportError as e:
        print(f"Import error: {str(e)}")
        print("Make sure GraphRAG Toolkit is properly linked in the lib directory.")
        return False
    except Exception as e:
        print(f"Setup failed: {str(e)}")
        return False

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Setup GraphRAG Toolkit integration with Neptune Analytics")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Running in verbose mode")
    
    if setup_graphrag():
        print("Setup completed successfully")
        sys.exit(0)
    else:
        print("Setup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
