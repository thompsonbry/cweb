#!/usr/bin/env python3
"""
Script to test connection to Neptune Analytics and perform basic operations.
"""

import os
import sys
import uuid
import numpy as np
from dotenv import load_dotenv
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import T, P, Cardinality

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from config.neptune_config import get_neptune_connection_string, VECTOR_DIMENSION

def test_neptune_connection():
    """Test connection to Neptune Analytics."""
    try:
        connection = DriverRemoteConnection(get_neptune_connection_string(), 'g')
        g = traversal().withRemote(connection)
        
        print("✅ Successfully connected to Neptune Analytics")
        
        # Test basic query
        count = g.V().count().next()
        print(f"✅ Graph contains {count} vertices")
        
        # Create a test vertex
        test_id = f"test-{uuid.uuid4()}"
        g.addV('TestVertex').property(T.id, test_id).property('name', 'Test Vertex').next()
        print(f"✅ Created test vertex with ID: {test_id}")
        
        # Verify the vertex was created
        result = g.V(test_id).values('name').next()
        print(f"✅ Retrieved vertex name: {result}")
        
        # Test vector search capability
        print("\nTesting vector search capability...")
        vector_test_id = f"vector-test-{uuid.uuid4()}"
        
        # Create a random vector
        vector = np.random.rand(VECTOR_DIMENSION).tolist()
        
        # Create a vertex with a vector property
        g.addV('VectorVertex').property(T.id, vector_test_id) \
            .property('name', 'Vector Test') \
            .property('embedding', vector) \
            .next()
        print(f"✅ Created vector test vertex with ID: {vector_test_id}")
        
        # Create a vector search query
        query_vector = np.random.rand(VECTOR_DIMENSION).tolist()
        
        try:
            # Attempt a vector search
            result = g.withSideEffect('vector', query_vector) \
                .V().hasLabel('VectorVertex') \
                .order().by('embedding', 'vector') \
                .limit(5) \
                .valueMap(True) \
                .toList()
            
            print(f"✅ Vector search successful, returned {len(result)} results")
            
        except Exception as e:
            print(f"❌ Vector search failed: {e}")
        
        # Clean up test vertices
        g.V(test_id).drop().iterate()
        g.V(vector_test_id).drop().iterate()
        print("✅ Cleaned up test vertices")
        
        # Close the connection
        connection.close()
        print("✅ Connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Neptune Analytics: {e}")
        return False

if __name__ == "__main__":
    if not os.getenv('NEPTUNE_ENDPOINT'):
        print("❌ NEPTUNE_ENDPOINT environment variable is not set")
        sys.exit(1)
        
    print(f"Testing connection to Neptune Analytics at {os.getenv('NEPTUNE_ENDPOINT')}")
    success = test_neptune_connection()
    
    if success:
        print("\n✅ All tests completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Tests failed")
        sys.exit(1)
