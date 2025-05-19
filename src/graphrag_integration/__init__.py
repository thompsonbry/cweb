"""
GraphRAG Integration Package

This package provides integration between the GraphRAG toolkit and Neptune Analytics
for fact extraction and knowledge graph building.
"""

from .config import GraphRAGConfig
from .neptune_analytics_adapter import NeptuneAnalyticsAdapter

__all__ = ['GraphRAGConfig', 'NeptuneAnalyticsAdapter']
