# HyperIBIS PlantUML Diagram

## Overview

This file contains a PlantUML representation of the HyperIBIS model. PlantUML is a tool that allows you to create UML diagrams from a text-based description language.

## How to View the Diagram

To render the PlantUML diagram, you have several options:

1. **Online PlantUML Editor**: 
   - Visit [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
   - Copy and paste the content of the `.puml` file

2. **VS Code with PlantUML Extension**:
   - Install the PlantUML extension for VS Code
   - Open the `.puml` file and use Alt+D to preview

3. **Command Line**:
   - Install PlantUML (requires Java)
   - Run: `java -jar plantuml.jar HyperIBIS_PlantUML.puml`

## Diagram Description

The PlantUML diagram represents the HyperIBIS model with the following components:

### Base Classes
- `Resource`: Base class for most objects in the model
- `EvidentiarySite`: Base class for sites that emit or collect evidence
- `Emitter`: Sites that distribute evidence
- `Collector`: Sites that receive evidence

### Main Classes
- `Problem`: Container for related issues
- `Issue`: Represents a question to be resolved
- `Position`: Represents a possible answer to an issue
- `Argument`: Links evidence to positions
- `Assessment`: Provides personalized interpretations of evidence

### Specialized Issue Types
- `MutexIssue`: Positions are mutually exclusive
- `Hypothesis`: Special case with a single position having two truth states
- `WorldIssue`: Each position represents a different possible world

### Evidentiary Site Types
- `EPlus`: Distributes evidence based on truth
- `EMinus`: Distributes evidence based on falsification
- `CPlus`: Collects supporting evidence
- `CMinus`: Collects falsifying evidence
- Specialized sites: `EvidenceSite`, `SupportSite`, `RebuttalSite`, `ConclusionSite`

### Key Relationships
- Problems contain Issues
- Issues have Positions
- Positions have four evidentiary sites
- Arguments have three evidentiary sites
- Resources may have one evidentiary site
- Evidence flows from Emitters to Collectors via EvidentiaryLinks
- Assessments are associated with Emitters and EvidentiaryLinks

## Notes

This diagram captures the structural relationships in the HyperIBIS model but does not represent the dynamic behavior of evidence propagation or inference algorithms. It serves as a visual reference for understanding the components and their relationships within the model.
