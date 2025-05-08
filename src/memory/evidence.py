"""
Evidence management module for storing and retrieving evidence in Neptune Analytics.
"""

import uuid
from typing import Dict, List, Optional, Any
import boto3
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

from config.neptune_config import (
    GRAPHRAG_CONFIG, 
    EVIDENCE_LABEL, 
    get_neptune_connection_string
)


class Evidence:
    """
    Class representing a piece of evidence in the system.
    """
    
    def __init__(
        self, 
        content: str, 
        source: str, 
        metadata: Optional[Dict[str, Any]] = None,
        evidence_id: Optional[str] = None
    ):
        """
        Initialize an Evidence object.
        
        Args:
            content: The content of the evidence
            source: The source of the evidence
            metadata: Additional metadata about the evidence
            evidence_id: Optional ID for the evidence, generated if not provided
        """
        self.content = content
        self.source = source
        self.metadata = metadata or {}
        self.evidence_id = evidence_id or f"evidence-{str(uuid.uuid4())}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the evidence to a dictionary.
        
        Returns:
            Dict representation of the evidence
        """
        return {
            "id": self.evidence_id,
            "content": self.content,
            "source": self.source,
            "metadata": self.metadata,
            "label": EVIDENCE_LABEL
        }


class EvidenceStore:
    """
    Store for managing evidence in Neptune Analytics.
    """
    
    def __init__(self):
        """
        Initialize the EvidenceStore with Neptune connections.
        """
        # Initialize Gremlin connection for graph operations
        self.connection = DriverRemoteConnection(get_neptune_connection_string(), 'g')
        self.g = traversal().withRemote(self.connection)
        
        # Initialize GraphRAG components when needed
        self._vector_store = None
        self._graph_store = None
    
    @property
    def vector_store(self):
        """Lazy initialization of vector store"""
        if self._vector_store is None:
            from graphrag.vector_store.neptune import NeptuneVectorStore
            
            vector_config = GRAPHRAG_CONFIG["vector_store"]["config"]
            self._vector_store = NeptuneVectorStore(
                endpoint=vector_config["endpoint"],
                port=vector_config["port"],
                region=vector_config["region"],
                vector_dimension=vector_config["vector_dimension"]
            )
        return self._vector_store
    
    @property
    def graph_store(self):
        """Lazy initialization of graph store"""
        if self._graph_store is None:
            from graphrag.graph_store.neptune import NeptuneGraphStore
            
            graph_config = GRAPHRAG_CONFIG["graph_store"]["config"]
            self._graph_store = NeptuneGraphStore(
                endpoint=graph_config["endpoint"],
                port=graph_config["port"],
                region=graph_config["region"],
                namespace=graph_config["namespace"]
            )
        return self._graph_store
    
    def add_evidence(self, evidence: Evidence, embedding: List[float]) -> str:
        """
        Add evidence to both vector store and graph.
        
        Args:
            evidence: The Evidence object to add
            embedding: Vector embedding of the evidence content
            
        Returns:
            ID of the added evidence
        """
        # Add to vector store
        vector_id = self.vector_store.add_vector(
            id=evidence.evidence_id,
            vector=embedding,
            metadata=evidence.to_dict()
        )
        
        # Add to graph store
        self.graph_store.add_vertex(
            label=EVIDENCE_LABEL,
            properties=evidence.to_dict()
        )
        
        return vector_id
    
    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """
        Retrieve evidence by ID.
        
        Args:
            evidence_id: ID of the evidence to retrieve
            
        Returns:
            Evidence object if found, None otherwise
        """
        result = self.g.V().hasLabel(EVIDENCE_LABEL).has('id', evidence_id).valueMap(True).toList()
        
        if not result:
            return None
        
        properties = result[0]
        return Evidence(
            content=properties.get('content', [''])[0],
            source=properties.get('source', [''])[0],
            metadata=properties.get('metadata', [{}])[0],
            evidence_id=properties.get('id')
        )
    
    def search_similar_evidence(self, query_embedding: List[float], top_k: int = 5) -> List[Evidence]:
        """
        Search for similar evidence using vector similarity.
        
        Args:
            query_embedding: Vector embedding of the query
            top_k: Number of results to return
            
        Returns:
            List of Evidence objects
        """
        results = self.vector_store.search_vectors(
            query_vector=query_embedding,
            top_k=top_k
        )
        
        evidence_list = []
        for result in results:
            metadata = result.get('metadata', {})
            evidence = Evidence(
                content=metadata.get('content', ''),
                source=metadata.get('source', ''),
                metadata=metadata.get('metadata', {}),
                evidence_id=metadata.get('id')
            )
            evidence_list.append(evidence)
        
        return evidence_list
    
    def close(self):
        """
        Close connections.
        """
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
