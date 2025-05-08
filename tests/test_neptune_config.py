"""
Unit tests for Neptune configuration.
"""

import unittest
import os
from unittest.mock import patch
import sys
import importlib

# Add the project root to the path so we can import the config module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestNeptuneConfig(unittest.TestCase):
    """Test cases for Neptune configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Save original environment variables
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Reload the config module to reset any changes
        if 'config.neptune_config' in sys.modules:
            importlib.reload(sys.modules['config.neptune_config'])
    
    @patch.dict(os.environ, {
        'NEPTUNE_ENDPOINT': 'test-endpoint.neptune.amazonaws.com',
        'NEPTUNE_PORT': '8182',
        'NEPTUNE_AUTH_MODE': 'IAM',
        'NEPTUNE_REGION': 'us-west-2'
    })
    def test_config_from_env(self):
        """Test loading configuration from environment variables."""
        # Import the module after setting environment variables
        from config.neptune_config import (
            NEPTUNE_ENDPOINT, NEPTUNE_PORT, NEPTUNE_AUTH_MODE, NEPTUNE_REGION
        )
        
        self.assertEqual(NEPTUNE_ENDPOINT, 'test-endpoint.neptune.amazonaws.com')
        self.assertEqual(NEPTUNE_PORT, '8182')
        self.assertEqual(NEPTUNE_AUTH_MODE, 'IAM')
        self.assertEqual(NEPTUNE_REGION, 'us-west-2')
    
    @patch.dict(os.environ, {
        'NEPTUNE_ENDPOINT': 'test-endpoint.neptune.amazonaws.com',
        'NEPTUNE_AUTH_MODE': 'IAM'
    })
    def test_config_defaults(self):
        """Test default values for configuration."""
        # Import the module after setting environment variables
        from config.neptune_config import (
            NEPTUNE_ENDPOINT, NEPTUNE_PORT, NEPTUNE_AUTH_MODE, NEPTUNE_REGION
        )
        
        self.assertEqual(NEPTUNE_ENDPOINT, 'test-endpoint.neptune.amazonaws.com')
        self.assertEqual(NEPTUNE_PORT, '8182')  # Default value
        self.assertEqual(NEPTUNE_AUTH_MODE, 'IAM')
        self.assertEqual(NEPTUNE_REGION, 'us-west-2')  # Default value
    
    @patch.dict(os.environ, {
        'NEPTUNE_ENDPOINT': 'test-endpoint.neptune.amazonaws.com',
        'NEPTUNE_AUTH_MODE': 'IAM'
    })
    def test_connection_string_iam(self):
        """Test connection string with IAM authentication."""
        from config.neptune_config import get_neptune_connection_string
        
        connection_string = get_neptune_connection_string()
        self.assertEqual(
            connection_string,
            'wss://test-endpoint.neptune.amazonaws.com:8182/gremlin'
        )
    
    @patch.dict(os.environ, {
        'NEPTUNE_ENDPOINT': 'test-endpoint.neptune.amazonaws.com',
        'NEPTUNE_AUTH_MODE': 'DEFAULT'
    })
    def test_connection_string_default(self):
        """Test connection string with DEFAULT authentication."""
        from config.neptune_config import get_neptune_connection_string
        
        connection_string = get_neptune_connection_string()
        self.assertEqual(
            connection_string,
            'ws://test-endpoint.neptune.amazonaws.com:8182/gremlin'
        )
    
    @patch.dict(os.environ, {})
    def test_missing_endpoint(self):
        """Test error when NEPTUNE_ENDPOINT is missing."""
        from config.neptune_config import get_neptune_connection_string
        
        with self.assertRaises(ValueError):
            get_neptune_connection_string()
    
    def test_constants_defined(self):
        """Test that all required constants are defined."""
        from config.neptune_config import (
            VECTOR_DIMENSION, VECTOR_SIMILARITY_METRIC,
            GRAPH_NAMESPACE, EVIDENCE_LABEL, ARGUMENT_LABEL,
            STORY_LABEL, POSITION_LABEL, ISSUE_LABEL,
            SUPPORTS_REL, OPPOSES_REL, PART_OF_REL, ADDRESSES_REL,
            ISSUE_TYPES, CRITIQUE_TYPES, CORRECTION_TYPES
        )
        
        # Check vector configuration
        self.assertEqual(VECTOR_DIMENSION, 1024)
        self.assertEqual(VECTOR_SIMILARITY_METRIC, "cosine")
        
        # Check graph configuration
        self.assertEqual(GRAPH_NAMESPACE, "cweb")
        
        # Check node labels
        self.assertEqual(EVIDENCE_LABEL, "Evidence")
        self.assertEqual(ARGUMENT_LABEL, "Argument")
        self.assertEqual(STORY_LABEL, "Story")
        self.assertEqual(POSITION_LABEL, "Position")
        self.assertEqual(ISSUE_LABEL, "Issue")
        
        # Check relationship types
        self.assertEqual(SUPPORTS_REL, "SUPPORTS")
        self.assertEqual(OPPOSES_REL, "OPPOSES")
        self.assertEqual(PART_OF_REL, "PART_OF")
        self.assertEqual(ADDRESSES_REL, "ADDRESSES")
        
        # Check HyperIBIS constants
        self.assertIn('REGULAR', ISSUE_TYPES)
        self.assertIn('MUTEX', ISSUE_TYPES)
        self.assertIn('HYPOTHESIS', ISSUE_TYPES)
        self.assertIn('WORLD', ISSUE_TYPES)
        
        # Check metacognition constants
        self.assertIn('INCOMPLETENESS', CRITIQUE_TYPES)
        self.assertIn('CONFLICT', CRITIQUE_TYPES)
        self.assertIn('UNRELIABILITY', CRITIQUE_TYPES)
        
        self.assertIn('ELABORATION', CORRECTION_TYPES)
        self.assertIn('REVISION', CORRECTION_TYPES)
        self.assertIn('REJECTION', CORRECTION_TYPES)


if __name__ == '__main__':
    unittest.main()
