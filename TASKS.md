# CWEB Project Tasks

## Current Focus: Argument Extraction

We are currently working on extending the GraphRAG toolkit to extract and represent arguments from documents. This involves identifying claims, positions, and supporting/rebutting arguments from text.

### Completed Tasks

1. **Security Improvements**
   - Removed hardcoded Neptune Analytics graph IDs from Python scripts
   - Updated scripts to use environment variables for configuration
   - Created and updated .gitignore to prevent committing sensitive information
   - Verified scripts functionality after security changes
   - Merged changes from feature branch to main branch

2. **Initial Argument Extraction Implementation**
   - Created scripts for extracting arguments from text samples
   - Tested extraction on small document samples
   - Implemented stable ID generation for cross-document reference

### Current Challenges

1. **Extracting Substantive Claims**
   - Current extraction tends to identify meta-level claims about the paper itself rather than substantive claims about the subject matter
   - Need to improve prompts to focus on the actual arguments being made in the text
   - Must work in a domain-agnostic manner across different types of documents

2. **Resource Limitations**
   - Large documents cause memory issues (exit code 137)
   - Need to implement incremental processing with smaller chunks
   - Need to handle API rate limiting and retries

3. **Argument Quality**
   - Some extracted arguments are generic or speculative rather than grounded in the text
   - Need to improve the quality and depth of extracted arguments
   - Need better evaluation of argument strength and relevance

4. **Cross-Document Reference**
   - Need to identify and reference similar claims across multiple documents
   - Need to merge similar claims and establish connections between related arguments

5. **Integration with GraphRAG**
   - Need to integrate argument extraction with the existing GraphRAG workflow
   - Need to represent arguments in a graph structure for exploration and querying
   - **Inconsistent chunk identifiers** (mix of numeric like "1", "2" and symbolic like "chunk1") indicate lack of integration with GraphRAG's document processing pipeline
   - Need standardized chunk identification and tracking across the entire pipeline

### Next Steps

1. **Improve Prompt Engineering**
   - Refine prompts to extract substantive claims about the subject matter
   - Test prompts across different domains (academic papers, regulations, interpretations)
   - Ensure domain-agnostic extraction of arguments

2. **Implement Incremental Processing**
   - Process documents in smaller chunks to avoid memory issues
   - Save intermediate results to build up the complete model
   - Implement retry logic for API calls

3. **Develop Evaluation Framework**
   - Create metrics for assessing argument quality
   - Compare extracted arguments against manually identified ground truth
   - Measure precision, recall, and F1 score

4. **Implement Cross-Document Reference**
   - Develop methods to identify similar claims across documents
   - Create a registry of claims that can be referenced
   - Implement claim normalization and merging

5. **Integrate with GraphRAG**
   - Extend GraphRAG's graph schema to represent arguments
   - Implement visualization tools for exploring argument structures
   - Enable queries about argument relationships
