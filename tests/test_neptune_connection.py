"""
Tests for Neptune Analytics connection and basic operations.
"""

import os
import uuid
import pytest
import numpy as np
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import T, P, Cardinality

from config.neptune_config import get_neptune_connection_string, VECTOR_DIMENSION

# Skip tests if Neptune endpoint is not configured
skip_if_no_neptune = pytest.mark.skipif(
    os.getenv('NEPTUNE_ENDPOINT') is None,
    reason="NEPTUNE_ENDPOINT environment variable not set"
)

@skip_if_no_neptune
class TestNeptuneConnection:
    """Test Neptune Analytics connection and basic operations."""
    
    @classmethod
    def setup_class(cls):
        """Set up the connection to Neptune Analytics."""
        try:
            cls.connection = DriverRemoteConnection(get_neptune_connection_string(), 'g')
            cls.g = traversal().withRemote(cls.connection)
            print("Connected to Neptune Analytics")
        except Exception as e:
            pytest.skip(f"Failed to connect to Neptune Analytics: {e}")
    
    @classmethod
    def teardown_class(cls):
        """Close the connection to Neptune Analytics."""
        if hasattr(cls, 'connection'):
            cls.connection.close()
    
    def test_connection(self):
        """Test that we can connect to Neptune Analytics."""
        # Simple query to verify connection
        result = self.g.V().limit(1).count().next()
        assert isinstance(result, int)
        print(f"Connection test passed. Found {result} vertices.")
    
    def test_create_vertex(self):
        """Test that we can create a vertex."""
        # Generate a unique ID for the test vertex
        test_id = f"test-{uuid.uuid4()}"
        
        # Create a vertex
        self.g.addV('TestVertex').property(T.id, test_id).property('name', 'Test Vertex').next()
        
        # Verify the vertex was created
        result = self.g.V(test_id).values('name').next()
        assert result == 'Test Vertex'
        print(f"Created vertex with ID {test_id}")
        
        # Clean up
        self.g.V(test_id).drop().iterate()
    
    def test_vector_search(self):
        """Test vector search functionality."""
        # Generate a unique ID for the test vertex
        test_id = f"vector-test-{uuid.uuid4()}"
        
        # Create a random vector
        vector = np.random.rand(VECTOR_DIMENSION).tolist()
        
        # Create a vertex with a vector property
        self.g.addV('VectorVertex').property(T.id, test_id) \
            .property('name', 'Vector Test') \
            .property('embedding', vector) \
            .next()
        
        # Create a vector search query
        query_vector = np.random.rand(VECTOR_DIMENSION).tolist()
        
        try:
            # Attempt a vector search
            # Note: This assumes Neptune Analytics has vector search enabled
            result = self.g.withSideEffect('vector', query_vector) \
                .V().hasLabel('VectorVertex') \
                .order().by('embedding', 'vector') \
                .limit(5) \
                .valueMap(True) \
                .toList()
            
            assert len(result) > 0
            print(f"Vector search returned {len(result)} results")
            
        except Exception as e:
            pytest.fail(f"Vector search failed: {e}")
        finally:
            # Clean up
            self.g.V(test_id).drop().iterate()
