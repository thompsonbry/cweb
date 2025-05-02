# HyperIBIS Model - Combined ASCII Diagram

```
                                  +----------------+
                                  |    Problem     |
                                  +----------------+
                                          |
                                          v
                  +---------------------+----------------+---------------------+
                  |                     |                |                     |
                  v                     v                v                     v
         +----------------+    +----------------+    +----------------+    +----------------+
         |  Regular Issue |    |   Mutex Issue  |    |   Hypothesis   |    |  World Issue   |
         +----------------+    +----------------+    +----------------+    +----------------+
                  |                     |                |                     |
                  |                     |                |                     |
                  v                     v                v                     v
         +----------------+    +----------------+    +----------------+    +----------------+
         |   Positions    |    |   Positions    |    |   Position     |    |   Positions    |
         | (Any number)   |    | (Mutually      |    | (Single with   |    | (Each is a     |
         |                |    |  exclusive)     |    |  two states)   |    |  possible world)|
         +----------------+    +----------------+    +----------------+    +----------------+
                  |                     |                |                     |
                  +---------------------+----------------+---------------------+
                                          |
                                          v
                                  +----------------+
                                  |   Position     |
                                  +----------------+
                                          |
            +-------------------------+---+---+-------------------------+
            |                         |       |                         |
            v                         v       v                         v
    +---------------+          +----------+          +----------+          +---------------+
    |    CPlus      |          |  CMinus  |          |  EPlus   |          |    EMinus     |
    | (Collector+)  |          | (Coll-)  |          | (Emit+)  |          |  (Emitter-)   |
    +---------------+          +----------+          +----------+          +---------------+
            ^                         ^       |                         |
            |                         |       |                         |
            |                         |       v                         v
    +---------------+          +----------+          +----------+          +---------------+
    |   Arguments   |<---------| Evidence |          | Evidence |--------->|   Arguments   |
    | (Supporting)  |          | (Web     |          | (Web     |          | (Rebutting)   |
    +---------------+          | Resource)|          | Resource)|          +---------------+
            |                  +----------+          +----------+                 |
            |                                                                     |
            v                                                                     v
    +---------------+                                                      +---------------+
    | ConclusionSite|                                                      | ConclusionSite|
    |    (e+)       |                                                      |    (e+)       |
    +---------------+                                                      +---------------+
            |                                                                     |
            |                                                                     |
            v                                                                     v
    +--------------------------------------------------+--------------------------------------------------+
    |                                                  |                                                  |
    |                                                  |                                                  |
    v                                                  v                                                  v
+----------+                                      +----------+                                      +----------+
| Assessor1|                                      | Assessor2|                                      | AssessorN|
+----------+                                      +----------+                                      +----------+
    |                                                  |                                                  |
    v                                                  v                                                  v
+----------+                                      +----------+                                      +----------+
|Assessment|                                      |Assessment|                                      |Assessment|
| -Belief  |                                      | -Belief  |                                      | -Belief  |
| -ExpVal  |                                      | -ExpVal  |                                      | -ExpVal  |
| -Strength|                                      | -Strength|                                      | -Strength|
+----------+                                      +----------+                                      +----------+
```

## Diagram Explanation

This ASCII diagram represents the combined HyperIBIS model based on both the DTD and PDF documentation:

### Top Level Structure
- **Problem**: Container for related issues and resources
- **Issue Types**: Four types of issues (Regular, Mutex, Hypothesis, World)
- **Positions**: Different configurations based on issue type

### Evidentiary Network
- **Position Sites**: Each position has four evidentiary sites:
  - CPlus (c+): Collects supporting evidence
  - CMinus (c-): Collects falsifying evidence
  - EPlus (e+): Emits evidence based on truth
  - EMinus (e-): Emits evidence based on falsification

- **Arguments**: Connect positions and evidence
  - Supporting arguments flow through CPlus collectors
  - Rebutting arguments flow through CMinus collectors
  - Both emit through ConclusionSite (e+)

- **Evidence**: Web resources that can be linked into the model

### Assessment Layer
- **Assessors**: Users or groups who provide assessments
- **Assessments**: Three types for each assessor:
  - Belief: Confidence in a proposition
  - Expected Value: Utility if proposition is true
  - Strength: Weight of evidentiary links

The diagram shows how evidence flows through the network, with different assessors potentially having different interpretations of the same evidence. This enables the collaborative, multi-perspective nature of the HyperIBIS model.
