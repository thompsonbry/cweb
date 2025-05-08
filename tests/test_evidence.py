"""
Unit tests for the Evidence module.
"""

import unittest
import uuid
from unittest.mock import patch, MagicMock
from src.memory.evidence import Evidence, EvidenceStore


class TestEvidence(unittest.TestCase):
    """Test cases for the Evidence class."""
    
    def test_evidence_initialization(self):
        """Test that Evidence objects are initialized correctly."""
        content = "Test content"
        source = "Test source"
        metadata = {"key": "value"}
        
        # Test with provided ID
        evidence_id = "test-id-123"
        evidence = Evidence(content, source, metadata, evidence_id)
        self.assertEqual(evidence.content, content)
        self.assertEqual(evidence.source, source)
        self.assertEqual(evidence.metadata, metadata)
        self.assertEqual(evidence.evidence_id, evidence_id)
        
        # Test with auto-generated ID
        evidence = Evidence(content, source, metadata)
        self.assertEqual(evidence.content, content)
        self.assertEqual(evidence.source, source)
        self.assertEqual(evidence.metadata, metadata)
        self.assertTrue(evidence.evidence_id.startswith("evidence-"))
        self.assertTrue(uuid.UUID(evidence.evidence_id.replace("evidence-", ""), version=4))
    
    def test_to_dict(self):
        """Test the to_dict method."""
        content = "Test content"
        source = "Test source"
        metadata = {"key": "value"}
        evidence_id = "test-id-123"
        
        evidence = Evidence(content, source, metadata, evidence_id)
        evidence_dict = evidence.to_dict()
        
        self.assertEqual(evidence_dict["id"], evidence_id)
        self.assertEqual(evidence_dict["content"], content)
        self.assertEqual(evidence_dict["source"], source)
        self.assertEqual(evidence_dict["metadata"], metadata)
        self.assertEqual(evidence_dict["label"], "Evidence")


class TestEvidenceStore(unittest.TestCase):
    """Test cases for the EvidenceStore class."""
    
    @patch('src.memory.evidence.DriverRemoteConnection')
    @patch('src.memory.evidence.traversal')
    def setUp(self, mock_traversal, mock_connection):
        """Set up test fixtures."""
        self.mock_traversal = mock_traversal
        self.mock_connection = mock_connection
        self.mock_g = MagicMock()
        mock_traversal.return_value.withRemote.return_value = self.mock_g
        
        self.evidence_store = EvidenceStore()
    
    def test_initialization(self):
        """Test that EvidenceStore is initialized correctly."""
        self.assertIsNotNone(self.evidence_store.connection)
        self.assertIsNotNone(self.evidence_store.g)
    
    @patch('src.memory.evidence.NeptuneVectorStore')
    def test_vector_store_lazy_initialization(self, mock_vector_store):
        """Test lazy initialization of vector store."""
        # Access vector_store property to trigger lazy initialization
        vector_store = self.evidence_store.vector_store
        
        # Verify NeptuneVectorStore was instantiated
        mock_vector_store.assert_called_once()
        self.assertIsNotNone(vector_store)
    
    @patch('src.memory.evidence.NeptuneGraphStore')
    def test_graph_store_lazy_initialization(self, mock_graph_store):
        """Test lazy initialization of graph store."""
        # Access graph_store property to trigger lazy initialization
        graph_store = self.evidence_store.graph_store
        
        # Verify NeptuneGraphStore was instantiated
        mock_graph_store.assert_called_once()
        self.assertIsNotNone(graph_store)
    
    def test_add_evidence(self):
        """Test adding evidence to the store."""
        # Mock the vector_store and graph_store
        self.evidence_store._vector_store = MagicMock()
        self.evidence_store._graph_store = MagicMock()
        
        # Create test evidence
        evidence = Evidence("Test content", "Test source")
        embedding = [0.1, 0.2, 0.3]
        
        # Add evidence
        result = self.evidence_store.add_evidence(evidence, embedding)
        
        # Verify vector_store.add_vector was called
        self.evidence_store._vector_store.add_vector.assert_called_once_with(
            id=evidence.evidence_id,
            vector=embedding,
            metadata=evidence.to_dict()
        )
        
        # Verify graph_store.add_vertex was called
        self.evidence_store._graph_store.add_vertex.assert_called_once_with(
            label="Evidence",
            properties=evidence.to_dict()
        )
    
    def test_get_evidence(self):
        """Test retrieving evidence by ID."""
        # Mock the Gremlin traversal
        mock_result = [{'id': 'evidence-123', 'content': ['Test content'], 'source': ['Test source'], 'metadata': [{}]}]
        self.mock_g.V().hasLabel().has().valueMap().toList.return_value = mock_result
        
        # Get evidence
        evidence = self.evidence_store.get_evidence("evidence-123")
        
        # Verify the result
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence.evidence_id, 'evidence-123')
        self.assertEqual(evidence.content, 'Test content')
        self.assertEqual(evidence.source, 'Test source')
    
    def test_search_similar_evidence(self):
        """Test searching for similar evidence."""
        # Mock the vector_store
        self.evidence_store._vector_store = MagicMock()
        mock_results = [
            {'metadata': {'id': 'evidence-1', 'content': 'Content 1', 'source': 'Source 1', 'metadata': {}}},
            {'metadata': {'id': 'evidence-2', 'content': 'Content 2', 'source': 'Source 2', 'metadata': {}}}
        ]
        self.evidence_store._vector_store.search_vectors.return_value = mock_results
        
        # Search for similar evidence
        query_embedding = [0.1, 0.2, 0.3]
        results = self.evidence_store.search_similar_evidence(query_embedding, top_k=2)
        
        # Verify search_vectors was called
        self.evidence_store._vector_store.search_vectors.assert_called_once_with(
            query_vector=query_embedding,
            top_k=2
        )
        
        # Verify the results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].evidence_id, 'evidence-1')
        self.assertEqual(results[0].content, 'Content 1')
        self.assertEqual(results[1].evidence_id, 'evidence-2')
        self.assertEqual(results[1].content, 'Content 2')
    
    def test_close(self):
        """Test closing the connection."""
        self.evidence_store.close()
        self.evidence_store.connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
