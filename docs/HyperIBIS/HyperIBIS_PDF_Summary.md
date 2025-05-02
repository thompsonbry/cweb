# HyperIBIS Abstract Model Summary (from PDF)

## Introduction

The HyperIBIS architecture extends the standard IBIS (Issue-Based Information System) model to support inference about belief and expected utility in formal argument models using an open hypertext architecture. While traditional IBIS models provide a formal model of argument following Toulmin's work for the United Nations in the 1950s, HyperIBIS extends this by:

1. Incorporating an open hypertext model that allows any addressable web resource to be interpreted as evidence in an argument
2. Developing the notion of beliefs, assumptions, value judgments, and expected utility as an elaboration of the basic IBIS graph

The document provides a non-normative abstract model for the HyperIBIS architecture, intended to inform specific implementations without requiring decomposition into a specific object model. A concrete implementation has been developed as part of the Cognitive Web effort, which is a semantic web initiative focused on collaborative, process-oriented decision-making.

## Class Hierarchy

Most objects in HyperIBIS are resources, enabling:
- HyperIBIS models to comment on themselves
- HyperIBIS models to incorporate references to issues, positions, and arguments in other HyperIBIS models

The class hierarchy includes:
- Resource (base class)
- Issue, Position, Argument (core IBIS elements)
- MutexIssue, Hypothesis, WorldIssue (specialized issue types)
- EvidentiaryLink, EvidentiarySite, Emitter, Collector (evidentiary components)
- Assessment, Assessor, Value (evaluation components)
- Various site types (EPlus, EMinus, CPlus, CMinus, ConclusionSite, EvidenceSite, RebuttalSite, SupportSite)

## Core Relationships

### Issues and Positions

- Each issue essentially asks a question
- Positions on an issue enumerate possible answers to that question
- Each position belongs to one and only one issue

### Specialized Issue Types

1. **Mutex Issue**
   - Positions are mutually exclusive (only one can be true)

2. **Hypothesis**
   - Special case of a Mutex Issue constrained to have only two possible truth states
   - Modeled using a single position
   - Support for the position is support for the hypothesis
   - Support for falsification of the position is support for negation of the hypothesis

3. **World Issue**
   - Each position represents a different possible world
   - Supports systematic reasoning about sets of coherent assumptions ("worlds")
   - Asks the question "Which world is true?"
   - Enables conditional dependency in the IBIS model based on the world that is currently believed
   - Allows for "what if" analysis by assuming a particular world is true and seeing the impact on evidence and expected value

## Evidentiary Network

### Evidentiary Links and Sites

Evidence is propagated from Emitters to Collectors in a directed graph. The evidentiary sites can be:

1. **Emitters** (distribute evidence):
   - EPlus (e+): Distributes combined evidence based on the truth of a proposition
   - EMinus (e-): Distributes combined evidence based on the falsification of a proposition

2. **Collectors** (receive evidence):
   - CPlus (c+): Collects evidence that supports a proposition
   - CMinus (c-): Collects evidence that supports the falsification of a proposition

### Site Configurations

1. **Positions** have four evidentiary sites:
   - CPlus (c+): Collects evidence supporting the truth of the position
   - CMinus (c-): Collects evidence supporting the falsification of the position
   - EPlus (e+): Distributes evidence based on the truth of the position
   - EMinus (e-): Distributes evidence based on the falsification of the position

2. **Arguments** have three evidentiary sites:
   - SupportSite (c+): Collects evidence supporting the argument
   - RebuttalSite (c-): Collects evidence defeating the argument
   - ConclusionSite (e+): Distributes evidence based on the truth of the argument

3. **Resources** may have one evidentiary site:
   - EvidenceSite (e+): Allows any resource to be linked as evidence in the IBIS model

## Assessments

Assessments associate floating-point values with evidentiary links or sites within the scope of a user or user group. There are three kinds:

1. Assessment of an evidentiary link's strength
2. Assessment of belief in the proposition represented by an emitter
3. Assessment of expected value if the proposition represented by an emitter is true

Key features of assessments:
- They are personalized interpretations of evidence and its impact
- Different users or groups can make differing assessments
- They enable representation of diverse beliefs about the structure and qualitative dimensions of the model
- They can identify divergent assessments to guide further model development

## Relationship to XTM (XML Topic Maps)

The document outlines basic identity relationships between the HyperIBIS Abstract Model and the XTM Abstract Model:
- Issues, Positions, and Arguments in HyperIBIS can be represented as Topics in XTM
- These relationships make it possible to use XTM to store metadata about the main entities in HyperIBIS

However, the document explicitly notes that:
- It does not define the HyperIBIS abstract model in terms of the XTM abstract model
- It does not define how to interchange a HyperIBIS model using XTM
- It does not define how a common implementation of HyperIBIS and XTM might be achieved

## Hypertext Integration

Hypertext is incorporated into the HyperIBIS architecture by associating an evidentiary site with a resource, making it possible to link any resource as evidence supporting positions in the IBIS model. Fine-grained annotations should be handled using an appropriate out-of-line resource indicator model, such as the XPointer specification.

## Inference and Analysis

The model supports:
- Inference algorithms to automatically detect the most likely world based on existing evidence
- "What if" analysis by assuming a particular world is true and seeing the impact on evidence propagation
- Critical thinking behaviors to identify divergent assessments and use that conflict to guide further model development
