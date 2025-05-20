# Contributing to CWEB Project

Thank you for your interest in contributing to the CWEB project. This document provides guidelines and best practices for development.

## Development Philosophy

### Problem-Solving Approach

1. **Fix problems, don't work around them**
   - When encountering issues, focus on resolving the root cause rather than changing project goals
   - Maintain the original objectives even when facing technical challenges
   - Invest time in proper debugging and resolution rather than implementing alternative approaches
   - Document the problem, solution, and lessons learned for future reference
   - Always carefully read error messages and logs to understand the actual issue

2. **No Mock Implementations**
   - DO NOT create mock or simulated implementations of dependencies
   - Always integrate with actual services and libraries
   - If a dependency is not available, fix the dependency issue rather than creating a mock
   - For testing, use proper testing frameworks and techniques like dependency injection

3. **Nothing works until it's tested**
   - All implementations must be verified through testing before being considered complete
   - Don't assume code works based on inspection alone
   - Write tests for critical functionality
   - Manually verify integrations with external systems
   - Document test procedures and expected outcomes
   - Test with realistic data and edge cases

## Code Standards

### General Principles

1. **Production-Ready Code**: All code should be written as if it's going directly to production. This means:
   - Proper error handling
   - Comprehensive logging
   - Performance considerations
   - Security best practices

2. **Documentation**: All code should be well-documented:
   - Clear function/method docstrings
   - Module-level documentation
   - Architecture documentation for larger components
   - Usage examples where appropriate

3. **Testing**: All code should have appropriate tests:
   - Unit tests for individual functions/methods
   - Integration tests for component interactions
   - End-to-end tests for critical workflows

### Code Style and Structure

1. **Python Best Practices**:
   - Follow PEP 8 style guidelines
   - Use type hints
   - Organize imports properly
   - Use meaningful variable and function names

2. **Project Structure**:
   - Keep related functionality in appropriate modules
   - Maintain clear separation of concerns
   - Use consistent naming conventions

3. **Configuration Management**:
   - Use environment variables for configuration
   - Provide example configuration files
   - Document all configuration options

## GraphRAG Integration Guidelines

1. **Direct Integration Only**:
   - Always integrate directly with the GraphRAG Toolkit
   - Ensure proper installation and configuration of the toolkit
   - Resolve any dependency or import issues directly

2. **Neptune Analytics Integration**:
   - Use Neptune Analytics for both graph and vector storage
   - Configure with the specified graph ID: `g-k2n0lshd74` in region `us-west-2`
   - Implement proper IAM authentication

3. **Error Handling**:
   - Implement comprehensive error handling for all GraphRAG and Neptune operations
   - Log detailed error information for debugging
   - Provide clear error messages to users

4. **Performance Considerations**:
   - Be mindful of large document processing
   - Implement batching for large operations
   - Consider caching strategies where appropriate

## Dependency Management

1. **Explicit Dependencies**:
   - All dependencies should be explicitly declared in requirements files
   - Pin dependency versions to ensure reproducibility
   - Document any special installation requirements

2. **Dependency Resolution**:
   - When encountering dependency issues, resolve them properly
   - Document any workarounds needed for specific dependencies
   - Consider using virtual environments for isolation

## Contribution Process

1. **Branch Strategy**:
   - Create feature branches for new work
   - Use pull requests for code review
   - Ensure CI/CD passes before merging

2. **Code Review**:
   - All code should be reviewed before merging
   - Address review comments promptly
   - Ensure code meets all guidelines before approval

3. **Documentation Updates**:
   - Update documentation when changing functionality
   - Keep README and other docs in sync with code changes
   - Document breaking changes clearly
