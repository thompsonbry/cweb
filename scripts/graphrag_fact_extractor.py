#!/usr/bin/env python3

"""
GraphRAG Fact Extractor

This script uses the GraphRAG toolkit to extract facts from documents.
It works with both text and PDF files.

Usage:
  uv run python scripts/graphrag_fact_extractor.py <file_path> [--output OUTPUT] [--verbose]
"""

import os
import sys
import json
import boto3
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Try to use pysqlite3 if available
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
    print("Using pysqlite3 as sqlite3")
except ImportError:
    print("pysqlite3 not available, using system sqlite3")

# Now try to import GraphRAG toolkit components
try:
    from graphrag_toolkit.lexical_graph import LexicalGraphIndex, TenantId, GraphRAGConfig, set_logging_config
    from llama_index.core import Document
    GRAPHRAG_AVAILABLE = True
    print("Successfully imported GraphRAG toolkit components")
except ImportError as e:
    print(f"Warning: Could not import GraphRAG toolkit: {e}")
    print(f"Make sure you're using Python 3.10+ with: uv run python scripts/graphrag_fact_extractor.py")
    GRAPHRAG_AVAILABLE = False

# Load environment variables
load_dotenv()

class DocumentReader:
    """Read documents from various file formats"""
    
    @staticmethod
    def read_text_file(file_path):
        """Read text from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file: {e}")
            return None
    
    @staticmethod
    def read_pdf_file(file_path):
        """Read text from a PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
                return text
        except ImportError:
            print("PyPDF2 not available. Cannot process PDF files.")
            return None
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return None
    
    @staticmethod
    def read_file(file_path):
        """Read text from a file based on its extension"""
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File {file_path} not found")
            return None
            
        if path.suffix.lower() == '.pdf':
            return DocumentReader.read_pdf_file(file_path)
        else:
            return DocumentReader.read_text_file(file_path)

class GraphRAGFactExtractor:
    """Extract facts from documents using GraphRAG toolkit"""
    
    def __init__(self):
        """Initialize the fact extractor with configuration"""
        if not GRAPHRAG_AVAILABLE:
            raise ImportError("GraphRAG toolkit not available")
            
        # Configure AWS region
        region = os.environ.get("AWS_REGION", "us-west-2")
        GraphRAGConfig.aws_region = region
        
        # Configure embedding model to match Neptune Analytics dimensions (1024)
        GraphRAGConfig.embed_model = "cohere.embed-english-v3"
        GraphRAGConfig.embed_dimensions = 1024
        
        # Configure LLM
        GraphRAGConfig.extraction_llm = "anthropic.claude-3-sonnet-20240229-v1:0"
        GraphRAGConfig.response_llm = "anthropic.claude-3-sonnet-20240229-v1:0"
        
        # Set logging
        set_logging_config('INFO')
        
        try:
            # Initialize GraphRAG components with Neptune Analytics
            from graphrag_toolkit.lexical_graph.storage import GraphStoreFactory, VectorStoreFactory
            
            # Get Neptune Analytics configuration from environment
            neptune_graph_id = os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID", "g-k2n0lshd74")
            neptune_region = os.environ.get("NEPTUNE_ANALYTICS_REGION", "us-west-2")
            
            # Set AWS region for GraphRAG
            GraphRAGConfig.aws_region = neptune_region
            
            # Create connection string
            neptune_connection = f"neptune-graph://{neptune_graph_id}"
            print(f"Connecting to Neptune Analytics: {neptune_connection}")
            
            # Create Neptune Analytics stores using factory methods
            graph_store = GraphStoreFactory.for_graph_store(neptune_connection)
            vector_store = VectorStoreFactory.for_vector_store(neptune_connection)
            
            # Create output directory
            output_dir = "/tmp/graphrag_output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Initialize with explicit parameters
            self.graph_index = LexicalGraphIndex(
                extraction_dir=output_dir,
                graph_store=graph_store,
                vector_store=vector_store
            )
            print("Successfully initialized GraphRAG components with Neptune Analytics")
        except Exception as e:
            print(f"Error initializing GraphRAG components: {e}")
            raise
    
    def process_document(self, file_path, document_id=None):
        """Process a document and extract facts"""
        path = Path(file_path)
        if not document_id:
            document_id = path.stem
            
        try:
            print(f"Processing document: {file_path}")
            
            # Read the document content
            content = DocumentReader.read_file(file_path)
            if not content:
                raise ValueError(f"Could not read content from {file_path}")
            
            # Create a Document object
            doc = Document(text=content, metadata={"source": str(path), "document_id": document_id})
            
            # Extract and build the graph
            self.graph_index.extract_and_build([doc], show_progress=True)
            
            # Extract facts and metadata
            facts = self._extract_facts_from_graph()
            
            return {
                "document_id": document_id,
                "graph": self.graph_index,
                "facts": facts
            }
            
        except Exception as e:
            print(f"Error processing document with GraphRAG: {e}")
            raise
    
    def _extract_facts_from_graph(self):
        """Extract facts from the built graph"""
        if not self.graph_index:
            return {}
            
        try:
            print("Extracting facts from Neptune Analytics graph...")
            
            # TODO: Implement fact extraction using execute_query API
            # This will be implemented in the next phase
            # For now, return empty collections
            return {
                "entities": {},
                "relationships": []
            }
            
        except Exception as e:
            print(f"Error extracting facts from graph: {e}")
            return {}
    
    def save_results(self, results, output_path):
        """Save results to a JSON file"""
        if not results:
            print("No results to save.")
            return False
            
        try:
            # Convert graph to serializable format if present
            if "graph" in results:
                # Extract serializable data from graph
                print("Preparing graph data for serialization...")
                
                # Since we can't directly access nodes and edges, save graph metadata
                graph_data = {
                    "metadata": {
                        "type": str(type(results["graph"])),
                        "stores": {
                            "graph_store": str(type(results["graph"].graph_store)) if hasattr(results["graph"], "graph_store") else "Unknown",
                            "vector_store": str(type(results["graph"].vector_store)) if hasattr(results["graph"], "vector_store") else "Unknown"
                        }
                    }
                }
                results["graph"] = graph_data
                
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
                
            print(f"Results saved to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error saving results: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Extract facts from documents using GraphRAG toolkit')
    parser.add_argument('file_path', help='Path to the document file (PDF or text)')
    parser.add_argument('--document-id', help='Unique identifier for the document', default=None)
    parser.add_argument('--output', '-o', help='Output file for the extracted facts', default=None)
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Starting fact extraction process...")
    
    # Process the document
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"Error: Document {file_path} not found")
        sys.exit(1)
    
    # Generate document ID if not provided
    document_id = args.document_id or file_path.stem
    
    try:
        # Create fact extractor
        extractor = GraphRAGFactExtractor()
        
        # Process the document
        results = extractor.process_document(file_path, document_id)
        
        if args.verbose:
            print(f"Document processed: {document_id}")
        
        # Save results
        output_path = args.output or f"/tmp/{document_id}_facts.json"
        extractor.save_results(results, output_path)
        
        print("Processing complete.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
