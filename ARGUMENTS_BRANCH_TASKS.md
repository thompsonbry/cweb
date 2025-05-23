# Argument Extraction Tasks

## Overview
This document outlines the tasks for implementing argument extraction from source documents in the "arguments" branch. The goal is to extend the existing fact extraction capabilities to identify argument models (HyperIBIS) from documents, improving functional agentic memory by providing access to non-local information that might not be discovered using keyword or vector search.

## Background
The HyperIBIS (Issue-Based Information System) model provides a structured approach to representing arguments, issues, and evidence. It extends traditional IBIS with belief and expected utility assessments. Our implementation will focus on extracting these argument structures from documents.

## Key Components to Extract
1. **Issues**: Questions or problems to be resolved
2. **Positions**: Possible answers to issues
3. **Arguments**: Supporting or rebutting evidence for positions
4. **Evidence**: Facts or statements that support arguments
5. **Assessments**: Evaluations of belief and expected utility

## Implementation Tasks

### 1. Create Argument Extraction Script
- [x] Create branch "arguments"
- [ ] Clone and modify the existing `graphrag_fact_extractor.py` script to create `graphrag_argument_extractor.py`
- [ ] Implement document chunking for better context management
- [ ] Develop LLM prompts specifically for argument identification

### 2. Develop Argument Extraction Pipeline
- [ ] Create `ArgumentExtractor` class that extends the existing extraction framework
- [ ] Implement methods to identify issues from document chunks
- [ ] Implement methods to extract positions on identified issues
- [ ] Implement methods to identify supporting and rebutting arguments
- [ ] Implement methods to link evidence to arguments

### 3. Design Argument-Specific LLM Prompts
- [ ] Create prompts to identify issues (questions/problems) in text
- [ ] Create prompts to extract positions (possible answers) on issues
- [ ] Create prompts to identify supporting and rebutting arguments
- [ ] Create prompts to assess belief and expected utility

### 4. Implement HyperIBIS Schema Integration
- [ ] Ensure extracted arguments conform to HyperIBIS schema
- [ ] Map extracted elements to appropriate Neptune Analytics graph structure
- [ ] Implement proper relationship types between argument elements
- [ ] Add metadata for belief and expected utility assessments

### 5. Develop Argument Visualization
- [ ] Create methods to export argument structures in a format suitable for visualization
- [ ] Implement basic visualization of argument structures
- [ ] Add interactive elements to explore argument graphs

### 6. Testing and Evaluation
- [ ] Test with `wcnn_1995.pdf` document
- [ ] Evaluate quality of extracted arguments
- [ ] Compare with manually identified arguments
- [ ] Measure coverage of key issues and positions

### 7. Documentation
- [ ] Document the argument extraction approach
- [ ] Create examples of extracted arguments
- [ ] Document integration with existing GraphRAG toolkit
- [ ] Update README with argument extraction capabilities

## Implementation Approach

### Argument Extraction Process
1. **Document Processing**:
   - Split document into semantic chunks
   - Process each chunk to identify potential issues, positions, and arguments
   - Merge and deduplicate findings across chunks

2. **Issue Identification**:
   - Use LLM to identify questions or problems discussed in the text
   - Ensure issues are formulated as clear, crisp questions
   - Classify issues as regular, mutex, hypothesis, or world issues

3. **Position Extraction**:
   - For each issue, identify possible positions (answers)
   - Ensure positions are declarative statements
   - Identify relationships between positions (contradictory, dependent)

4. **Argument Identification**:
   - Extract supporting and rebutting arguments for each position
   - Identify the warrant (justification) for each argument
   - Link arguments to specific text evidence

5. **Assessment Generation**:
   - Generate initial belief assessments based on text evidence
   - Estimate expected utility where possible
   - Record confidence levels for extracted elements

6. **Graph Construction**:
   - Create nodes for issues, positions, arguments, and evidence
   - Establish relationships according to HyperIBIS schema
   - Add assessment metadata to appropriate elements

## Next Steps
1. Implement the basic argument extraction script
2. Test with sample documents
3. Refine extraction prompts based on results
4. Integrate with Neptune Analytics graph
5. Develop visualization capabilities
