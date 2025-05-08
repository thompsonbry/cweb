# CWEB - Cognitive Web

CWEB is a project focused on implementing cognitive architectures for intelligent agents, with a focus on metacognitive capabilities.

## Neptune Analytics Integration

This branch integrates Neptune Analytics for persisting memories (evidence) and arguments in a graph database with vector search capabilities.
The CognitiveWeb is a human-centric web architecture comprised of semantic markup and fuzzy logics designed to support collaborative decision-making, critical thinking and conflict resolution processes. The goal of the CognitiveWeb is to extend human decision horizons by compensating for some intrinsic aspects of selective attention.

## Development Guidelines

### Testing Requirements

**IMPORTANT**: All code must pass the test suite before being committed. Run the test suite using:

```bash
python scripts/run_tests.py
```

**Testing Policy**:
- Tests MUST be run before any commit
- Tests MUST NOT be disabled without explicit authorization
- Implementation MUST NOT be mocked without explicit authorization
- Any test failures MUST be resolved before committing code

This strict testing policy ensures the reliability and stability of the codebase, particularly for the critical cognitive components that require high accuracy and consistency.
