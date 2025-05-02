# HyperIBIS Abstract Model Summary

## Overview

The HyperIBIS (Issue-Based Information System) is an XML-based framework designed to support collaborative decision-making, critical thinking, and conflict resolution processes. It extends the traditional IBIS model by incorporating an open hypertext architecture that allows any addressable web resource to be interpreted as evidence in an argument.

## Core Concepts

The HyperIBIS model is built around several key components that form a structured approach to representing arguments, issues, and evidence:

### Primary Elements

1. **Issue**
   - Represents a question or problem to be resolved
   - Can have multiple positions (possible answers)
   - Has a dependency attribute that defines relationships between positions (mutex or none)

2. **Position**
   - Represents a possible answer to an issue
   - Can be supported or rebutted by arguments
   - Contains assessments of belief and expected value

3. **Argument**
   - Links evidence to positions
   - Can support or rebut positions
   - Contains a warrant (justification for the argument)

4. **Assessment**
   - Provides personalized interpretations of evidence
   - Measures belief, expected value, or link strength
   - Can use crisp or fuzzy quantities

5. **Problem**
   - Container for related issues and resources
   - Represents the overall context for discussion

### Special Issue Types

1. **Mutex Issue**
   - Positions are mutually exclusive
   - Only one position can be true

2. **Hypothesis**
   - Special case of Mutex Issue with only two possible truth states
   - Modeled using a single position

3. **World Issue**
   - Each position represents a different possible world
   - Supports reasoning about sets of coherent assumptions

### Evidentiary Links

1. **Support**
   - Links evidence or positions to arguments that support a position
   - Can have assessments of strength

2. **Rebuttal**
   - Links evidence or positions to arguments that rebut a position
   - Can have assessments of strength

3. **Conclusion**
   - Links arguments to positions they support or rebut
   - Can have assessments of strength

## XML Structure

The HyperIBIS DTD defines an XML language for interchanging IBIS information with the following key elements:

- `<issue>` - Contains positions on a question
- `<position>` - Represents possible answers to an issue
- `<argument>` - Links evidence to positions
- `<support>` - Represents supporting evidence
- `<rebuttal>` - Represents contradicting evidence
- `<conclusion>` - Links arguments to positions
- `<assessment>` - Provides belief and value judgments
- `<problem>` - Groups related issues and resources
- `<resourceGraph>` - Container for interconnected resources

## ASCII Diagram of Core Relationships

```
                    +------------+
                    |  Problem   |
                    +------------+
                          |
                          v
                    +------------+
                    |   Issue    |<---------+
                    +------------+          |
                          |                 |
                          v                 |
                    +------------+          |
                    |  Position  |<----+    |
                    +------------+     |    |
                       ^      ^        |    |
                       |      |        |    |
          +------------+      +--------+    |
          |                   |             |
+-----------------+    +-----------------+  |
|    Argument     |    |    Argument     |  |
| (Supporting)    |    |   (Rebutting)   |  |
+-----------------+    +-----------------+  |
          |                   |             |
          v                   v             |
    +------------+     +------------+       |
    |  Support   |     |  Rebuttal  |       |
    +------------+     +------------+       |
          |                   |             |
          v                   v             |
    +------------+     +------------+       |
    |  Evidence  |     |  Evidence  |       |
    +------------+     +------------+       |
                                            |
    +------------+                          |
    | Assessment |-------------------------+
    +------------+
```

## Applications

The HyperIBIS model is designed to:

1. Support collaborative decision-making processes
2. Facilitate critical thinking and structured argumentation
3. Enable conflict resolution through formal representation of arguments
4. Extend human decision horizons by compensating for selective attention
5. Allow for personalized assessments of belief and expected utility
6. Support inference about belief in formal argument models

## Implementation

The HyperIBIS architecture has been implemented as part of the CognitiveWeb effort, which is a semantic web initiative focused on collaborative, process-oriented decision-making.

---

*This summary is based on the HyperIBIS DTD and related documentation from cognitiveweb.org.*
