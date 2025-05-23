#!/usr/bin/env python3

"""
GraphRAG Argument Extractor

This script extends the GraphRAG toolkit to extract argument models from documents.
It identifies issues, positions, supporting and rebutting arguments according to the HyperIBIS model.

Usage:
  uv run python scripts/graphrag_argument_extractor.py <file_path> [--output OUTPUT] [--verbose]
"""

import os
import sys
import json
import boto3
import argparse
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Tuple

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
    print(f"Make sure you're using Python 3.10+ with: uv run python scripts/graphrag_argument_extractor.py")
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

class DocumentChunker:
    """Split documents into semantic chunks for processing"""
    
    @staticmethod
    def chunk_text(text, chunk_size=1000, overlap=200):
        """Split text into overlapping chunks of approximately chunk_size characters"""
        if not text:
            return []
            
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Find a good breaking point near chunk_size
            end = min(start + chunk_size, text_length)
            
            # If we're not at the end, try to find a good breaking point
            if end < text_length:
                # Try to find a paragraph break
                paragraph_break = text.rfind('\n\n', start, end)
                if paragraph_break != -1 and paragraph_break > start + chunk_size // 2:
                    end = paragraph_break + 2
                else:
                    # Try to find a sentence break
                    sentence_break = max(
                        text.rfind('. ', start, end),
                        text.rfind('! ', start, end),
                        text.rfind('? ', start, end)
                    )
                    if sentence_break != -1 and sentence_break > start + chunk_size // 2:
                        end = sentence_break + 2
            
            # Add the chunk
            chunks.append(text[start:end])
            
            # Move to next chunk with overlap
            start = max(start, end - overlap)
            
            # If we can't make progress, force a break
            if start >= end:
                start = end
        
        return chunks

class ArgumentModel:
    """Class to represent the HyperIBIS argument model"""
    
    def __init__(self):
        self.issues = []
        self.positions = []
        self.arguments = []
        self.evidence = []
        self.assessments = []
        self.relationships = []
    
    def add_issue(self, issue_id, question, issue_type="regular", description=None):
        """Add an issue to the model"""
        self.issues.append({
            "id": issue_id,
            "question": question,
            "issue_type": issue_type,
            "description": description
        })
        return issue_id
    
    def add_position(self, position_id, issue_id, answer, description=None):
        """Add a position to the model"""
        self.positions.append({
            "id": position_id,
            "issue_id": issue_id,
            "answer": answer,
            "description": description
        })
        return position_id
    
    def add_argument(self, argument_id, position_id, warrant, is_supporting=True):
        """Add an argument to the model"""
        self.arguments.append({
            "id": argument_id,
            "position_id": position_id,
            "warrant": warrant,
            "is_supporting": is_supporting
        })
        return argument_id
    
    def add_evidence(self, evidence_id, argument_id, content, source=None):
        """Add evidence to the model"""
        self.evidence.append({
            "id": evidence_id,
            "argument_id": argument_id,
            "content": content,
            "source": source
        })
        return evidence_id
    
    def add_assessment(self, assessment_id, target_id, belief=None, expected_value=None, strength=None):
        """Add an assessment to the model"""
        self.assessments.append({
            "id": assessment_id,
            "target_id": target_id,
            "belief": belief,
            "expected_value": expected_value,
            "strength": strength
        })
        return assessment_id
    
    def add_relationship(self, source_id, target_id, relationship_type):
        """Add a relationship between elements"""
        self.relationships.append({
            "source_id": source_id,
            "target_id": target_id,
            "type": relationship_type
        })
    
    def to_dict(self):
        """Convert the model to a dictionary"""
        return {
            "issues": self.issues,
            "positions": self.positions,
            "arguments": self.arguments,
            "evidence": self.evidence,
            "assessments": self.assessments,
            "relationships": self.relationships
        }
    
    def from_dict(self, data):
        """Load the model from a dictionary"""
        self.issues = data.get("issues", [])
        self.positions = data.get("positions", [])
        self.arguments = data.get("arguments", [])
        self.evidence = data.get("evidence", [])
        self.assessments = data.get("assessments", [])
        self.relationships = data.get("relationships", [])

class ArgumentExtractor:
    """Extract argument models from documents"""
    
    def __init__(self):
        """Initialize the argument extractor"""
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
            neptune_graph_id = os.environ.get("NEPTUNE_ANALYTICS_GRAPH_ID")
            if not neptune_graph_id:
                raise ValueError("NEPTUNE_ANALYTICS_GRAPH_ID environment variable is required")
                
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
            
            # Initialize the argument model
            self.argument_model = ArgumentModel()
            
        except Exception as e:
            print(f"Error initializing ArgumentExtractor: {e}")
            raise
    
    def extract_arguments(self, file_path, document_id=None):
        """Extract arguments from a document"""
        path = Path(file_path)
        if not document_id:
            document_id = path.stem
            
        try:
            print(f"Processing document for argument extraction: {file_path}")
            
            # Read the document content
            content = DocumentReader.read_file(file_path)
            if not content:
                raise ValueError(f"Could not read content from {file_path}")
            
            # Split the document into chunks
            chunks = DocumentChunker.chunk_text(content)
            print(f"Document split into {len(chunks)} chunks")
            
            # Process each chunk to extract arguments
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}")
                self._process_chunk(chunk, document_id, chunk_id=i)
            
            # Merge and deduplicate findings
            self._merge_findings()
            
            # Create a Document object for GraphRAG
            doc = Document(text=content, metadata={"source": str(path), "document_id": document_id})
            
            # Extract and build the graph
            self.graph_index.extract_and_build([doc], show_progress=True)
            
            # Add argument model to the graph
            self._add_arguments_to_graph()
            
            return {
                "document_id": document_id,
                "graph": self.graph_index,
                "argument_model": self.argument_model.to_dict()
            }
            
        except Exception as e:
            print(f"Error extracting arguments: {e}")
            raise
    
    def _process_chunk(self, chunk, document_id, chunk_id):
        """Process a single chunk to extract arguments"""
        # Extract issues from the chunk
        issues = self._extract_issues(chunk)
        
        # For each issue, extract positions
        for issue in issues:
            issue_id = f"{document_id}_issue_{issue['id']}"
            self.argument_model.add_issue(
                issue_id=issue_id,
                question=issue['question'],
                issue_type=issue.get('issue_type', 'regular'),
                description=issue.get('description')
            )
            
            # Extract positions for this issue
            positions = self._extract_positions(chunk, issue['question'])
            
            for position in positions:
                position_id = f"{document_id}_position_{position['id']}"
                self.argument_model.add_position(
                    position_id=position_id,
                    issue_id=issue_id,
                    answer=position['answer'],
                    description=position.get('description')
                )
                
                # Extract supporting arguments
                supporting_args = self._extract_arguments(chunk, issue['question'], position['answer'], is_supporting=True)
                
                for arg in supporting_args:
                    arg_id = f"{document_id}_arg_sup_{arg['id']}"
                    self.argument_model.add_argument(
                        argument_id=arg_id,
                        position_id=position_id,
                        warrant=arg['warrant'],
                        is_supporting=True
                    )
                    
                    # Add evidence for this argument
                    if 'evidence' in arg:
                        evidence_id = f"{document_id}_evidence_{arg['id']}"
                        self.argument_model.add_evidence(
                            evidence_id=evidence_id,
                            argument_id=arg_id,
                            content=arg['evidence'],
                            source=f"Chunk {chunk_id}"
                        )
                
                # Extract rebutting arguments
                rebutting_args = self._extract_arguments(chunk, issue['question'], position['answer'], is_supporting=False)
                
                for arg in rebutting_args:
                    arg_id = f"{document_id}_arg_reb_{arg['id']}"
                    self.argument_model.add_argument(
                        argument_id=arg_id,
                        position_id=position_id,
                        warrant=arg['warrant'],
                        is_supporting=False
                    )
                    
                    # Add evidence for this argument
                    if 'evidence' in arg:
                        evidence_id = f"{document_id}_evidence_{arg['id']}"
                        self.argument_model.add_evidence(
                            evidence_id=evidence_id,
                            argument_id=arg_id,
                            content=arg['evidence'],
                            source=f"Chunk {chunk_id}"
                        )
    
    def _extract_issues(self, text):
        """Extract issues (questions/problems) from text using LLM"""
        try:
            # Create a prompt for the LLM to identify issues
            prompt = """
            Analyze the following text and identify the key issues, questions, or problems being discussed.
            For each issue:
            1. Formulate it as a clear, specific question
            2. Classify it as one of these types:
               - regular: A general issue with multiple possible answers
               - mutex: An issue where positions are mutually exclusive
               - hypothesis: A yes/no question with only two possible states
               - world: An issue where each position represents a different possible world
            3. Provide a brief description of the issue's context
            
            Format your response as a JSON array of objects with these fields:
            - id: A short identifier (e.g., "issue1")
            - question: The issue formulated as a question
            - issue_type: The classification (regular, mutex, hypothesis, world)
            - description: Brief context about the issue
            
            TEXT:
            {text}
            
            ISSUES (JSON format):
            """
            
            # Call the LLM to extract issues
            from graphrag_toolkit.llm import LLMClient
            llm_client = LLMClient()
            response = llm_client.complete(prompt.format(text=text))
            
            # Parse the JSON response
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                issues = json.loads(json_str)
                return issues
            else:
                # Try to extract JSON with more lenient pattern
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = f"[{json_match.group(0)}]"
                    issues = json.loads(json_str)
                    return issues
                
                print(f"Could not parse issues from LLM response: {response}")
                return []
                
        except Exception as e:
            print(f"Error extracting issues: {e}")
            return []
    
    def _extract_positions(self, text, issue):
        """Extract positions (possible answers) on an issue using LLM"""
        try:
            # Create a prompt for the LLM to identify positions
            prompt = """
            Analyze the following text and identify the different positions or viewpoints on this issue:
            
            ISSUE: {issue}
            
            For each position:
            1. Formulate it as a clear, declarative statement (an answer to the issue)
            2. Provide a brief description or explanation of the position
            
            Format your response as a JSON array of objects with these fields:
            - id: A short identifier (e.g., "position1")
            - answer: The position as a declarative statement
            - description: Brief explanation of the position
            
            TEXT:
            {text}
            
            POSITIONS (JSON format):
            """
            
            # Call the LLM to extract positions
            from graphrag_toolkit.llm import LLMClient
            llm_client = LLMClient()
            response = llm_client.complete(prompt.format(text=text, issue=issue))
            
            # Parse the JSON response
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                positions = json.loads(json_str)
                return positions
            else:
                # Try to extract JSON with more lenient pattern
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = f"[{json_match.group(0)}]"
                    positions = json.loads(json_str)
                    return positions
                    
                print(f"Could not parse positions from LLM response: {response}")
                return []
                
        except Exception as e:
            print(f"Error extracting positions: {e}")
            return []
    
    def _extract_arguments(self, text, issue, position, is_supporting=True):
        """Extract arguments for or against a position using LLM"""
        try:
            # Create a prompt for the LLM to identify arguments
            arg_type = "supporting" if is_supporting else "rebutting"
            prompt = """
            Analyze the following text and identify {arg_type} arguments for this position:
            
            ISSUE: {issue}
            POSITION: {position}
            
            For each {arg_type} argument:
            1. Provide a warrant (justification for why this argument {supports_or_rebuts} the position)
            2. Extract specific evidence from the text that backs this argument
            
            Format your response as a JSON array of objects with these fields:
            - id: A short identifier (e.g., "arg1")
            - warrant: The justification for why this argument {supports_or_rebuts} the position
            - evidence: Specific text evidence that backs this argument
            
            TEXT:
            {text}
            
            {ARG_TYPE} ARGUMENTS (JSON format):
            """
            
            supports_or_rebuts = "supports" if is_supporting else "rebuts"
            ARG_TYPE = "SUPPORTING" if is_supporting else "REBUTTING"
            
            # Call the LLM to extract arguments
            from graphrag_toolkit.llm import LLMClient
            llm_client = LLMClient()
            response = llm_client.complete(prompt.format(
                text=text, 
                issue=issue, 
                position=position, 
                arg_type=arg_type,
                supports_or_rebuts=supports_or_rebuts,
                ARG_TYPE=ARG_TYPE
            ))
            
            # Parse the JSON response
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                arguments = json.loads(json_str)
                return arguments
            else:
                # Try to extract JSON with more lenient pattern
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = f"[{json_match.group(0)}]"
                    arguments = json.loads(json_str)
                    return arguments
                    
                print(f"Could not parse arguments from LLM response: {response}")
                return []
                
        except Exception as e:
            print(f"Error extracting arguments: {e}")
            return []
    
    def _merge_findings(self):
        """Merge and deduplicate findings across chunks"""
        # This is a placeholder for more sophisticated merging logic
        # In a real implementation, we would:
        # 1. Identify similar issues and merge them
        # 2. Identify similar positions and merge them
        # 3. Identify similar arguments and merge them
        # 4. Update relationships accordingly
        pass
    
    def _add_arguments_to_graph(self):
        """Add the argument model to the Neptune Analytics graph"""
        try:
            # Create nodes for issues
            for issue in self.argument_model.issues:
                self._create_issue_node(issue)
            
            # Create nodes for positions and link to issues
            for position in self.argument_model.positions:
                self._create_position_node(position)
            
            # Create nodes for arguments and link to positions
            for argument in self.argument_model.arguments:
                self._create_argument_node(argument)
            
            # Create nodes for evidence and link to arguments
            for evidence in self.argument_model.evidence:
                self._create_evidence_node(evidence)
            
            # Create assessments and link to appropriate elements
            for assessment in self.argument_model.assessments:
                self._create_assessment_node(assessment)
            
        except Exception as e:
            print(f"Error adding arguments to graph: {e}")
    
    def _create_issue_node(self, issue):
        """Create a node for an issue in the graph"""
        query = f"""
        MERGE (i:Issue {{id: '{issue['id']}'}})
        SET i.question = '{issue['question']}',
            i.issue_type = '{issue['issue_type']}'
        """
        if issue.get('description'):
            query += f", i.description = '{issue['description']}'"
        
        try:
            self.graph_index.graph_store.execute_query(query)
        except Exception as e:
            print(f"Error creating issue node: {e}")
    
    def _create_position_node(self, position):
        """Create a node for a position in the graph"""
        query = f"""
        MERGE (p:Position {{id: '{position['id']}'}})
        SET p.answer = '{position['answer']}'
        """
        if position.get('description'):
            query += f", p.description = '{position['description']}'"
        
        query += f"""
        WITH p
        MATCH (i:Issue {{id: '{position['issue_id']}'}})
        MERGE (i)-[:HAS_POSITION]->(p)
        """
        
        try:
            self.graph_index.graph_store.execute_query(query)
        except Exception as e:
            print(f"Error creating position node: {e}")
    
    def _create_argument_node(self, argument):
        """Create a node for an argument in the graph"""
        query = f"""
        MERGE (a:Argument {{id: '{argument['id']}'}})
        SET a.warrant = '{argument['warrant']}'
        WITH a
        MATCH (p:Position {{id: '{argument['position_id']}'}})
        """
        
        if argument['is_supporting']:
            query += "MERGE (a)-[:SUPPORTS]->(p)"
        else:
            query += "MERGE (a)-[:REBUTS]->(p)"
        
        try:
            self.graph_index.graph_store.execute_query(query)
        except Exception as e:
            print(f"Error creating argument node: {e}")
    
    def _create_evidence_node(self, evidence):
        """Create a node for evidence in the graph"""
        query = f"""
        MERGE (e:Evidence {{id: '{evidence['id']}'}})
        SET e.content = '{evidence['content']}'
        """
        if evidence.get('source'):
            query += f", e.source = '{evidence['source']}'"
        
        query += f"""
        WITH e
        MATCH (a:Argument {{id: '{evidence['argument_id']}'}})
        MERGE (e)-[:PROVIDES_EVIDENCE]->(a)
        """
        
        try:
            self.graph_index.graph_store.execute_query(query)
        except Exception as e:
            print(f"Error creating evidence node: {e}")
    
    def _create_assessment_node(self, assessment):
        """Create a node for an assessment in the graph"""
        query = f"""
        MERGE (a:Assessment {{id: '{assessment['id']}'}})
        """
        
        if assessment.get('belief') is not None:
            query += f", a.belief = {assessment['belief']}"
        if assessment.get('expected_value') is not None:
            query += f", a.expected_value = {assessment['expected_value']}"
        if assessment.get('strength') is not None:
            query += f", a.strength = {assessment['strength']}"
        
        query += f"""
        WITH a
        MATCH (t {{id: '{assessment['target_id']}'}})
        MERGE (a)-[:ASSESSED_ON]->(t)
        """
        
        try:
            self.graph_index.graph_store.execute_query(query)
        except Exception as e:
            print(f"Error creating assessment node: {e}")
    
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
    parser = argparse.ArgumentParser(description='Extract argument models from documents using GraphRAG toolkit')
    parser.add_argument('file_path', help='Path to the document file (PDF or text)')
    parser.add_argument('--document-id', help='Unique identifier for the document', default=None)
    parser.add_argument('--output', '-o', help='Output file for the extracted arguments', default=None)
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Starting argument extraction process...")
    
    # Process the document
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"Error: Document {file_path} not found")
        sys.exit(1)
    
    # Generate document ID if not provided
    document_id = args.document_id or file_path.stem
    
    try:
        # Create argument extractor
        extractor = ArgumentExtractor()
        
        # Process the document
        results = extractor.extract_arguments(file_path, document_id)
        
        if args.verbose:
            print(f"Document processed: {document_id}")
        
        # Save results
        output_path = args.output or f"output/{document_id}_arguments.json"
        extractor.save_results(results, output_path)
        
        print("Argument extraction complete.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
