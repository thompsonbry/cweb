# WCNN 1995 Paper Summary: Metacognitive Behavior in Adaptive Agents

## Citation

```bibtex
@inproceedings{thompson1995metacognitive,
  title={Metacognitive behavior in adaptive agents},
  author={Thompson, BB and Cohen, MS and Freeman, JT},
  booktitle={Proceedings of the World Congress on Neural Networks},
  volume={2},
  pages={266--273},
  year={1995}
}
```

## Overview

This summary covers the paper "Metacognitive Behavior in Adaptive Agents" by Bryan Thompson, Dr. Marvin Cohen, and Dr. Jared Freeman from Cognitive Technologies, Inc., which was presented at the World Congress on Neural Networks in 1995.

## Introduction

The paper presents a multidisciplinary architecture that combines research in cognitive science and connectionism to develop an integrated computational model for the acquisition and performance of recognitional and metacognitive skills in both human subjects and intelligent agents. The work builds on three key components:

1. The Recognition/Metacognition (R/M) model of human decision making
2. The SHRUTI model of reflexive reasoning in connectionist systems
3. Adaptive Critics, a connectionist model of behavior learning

The authors aim to develop a hybrid computational realization of the R/M model as a foundation for designing adaptive intelligent agents.

## Current Models of Decision-Making

The paper contrasts two different approaches to decision-making:

1. **Analytical Model** (e.g., Raiffa, 1968; Keeney and Raiffa, 1976):
   - Decision makers generate options, outcomes, and goals
   - Assess probabilities of outcomes and values of goals
   - Aggregate probabilities and values into scores for each option
   - Choose among options based on these scores
   - Use feedback to update future assessments

2. **Recognition Model** (Chase and Simon, 1973; Klein, 1993):
   - Experienced decision makers match perceptual cues to learned patterns
   - Patterns trigger specific responses
   - Success or failure alters stored relations between cues, patterns, and responses

The authors argue that neither model adequately accounts for human behavior in critical decision-making tasks, based on interviews with Naval officers and Army command staff. They observed that officers:
- Do not engage in exhaustive generation of outcomes or comparison of alternatives
- Weave coherent stories from events to describe intent and future actions
- Treat concordant and conflicting data differently
- Handle unfamiliar problems and update schemas in the face of novelty
- Juggle competing hypotheses and generate alternative interpretations of cues

## The Recognition/Metacognition (R/M) Model

The authors propose an alternative model that combines pattern recognition with strategies for facilitating recognition, verifying results, and constructing more adequate models when recognition fails. The R/M model consists of:

1. **Recognition Function**: Transforms perceived and internally generated data into a cognitive model of the situation and triggers associated actions or plans
   - In familiar situations, matches data to known patterns
   - In unfamiliar situations, relies on metacognitive processes

2. **Story Construction**: Decision makers construct causal structures (stories) to organize complex information
   - Components: initiating events → goals → actions → consequences
   - Naval officers construct stories involving assumptions of intent (reconnaissance, harassment, search and rescue, attack)

3. **Model Components**:
   - Situation recognition system
   - Gating function ("Quick Test")
   - Metacognitive processes (critiquing and correcting)

Processing is cyclical: a situation may be recognized, evaluated, modified, and re-evaluated before triggering an action.

## Hybrid Architecture for Agents with Metacognitive Behavior Learning

The proposed architecture consists of two cooperating adaptive critic architectures:

1. **Recognition Subsystem**: Focuses on recognitional modeling of reality, associated plans of action, and expected utility of outcomes
   - Uses a SHRUTI network for maintaining structured representations of evidence and relationships

2. **Metacognitive Subsystem**: Monitors, critiques, and corrects recognitional products and maintains coherent stories
   - Uses Backpropagated Adaptive Critics (BACs)

3. **Interface**: Traditional symbolic systems manage the interface between the recognitional and metacognitive subsystems

### Key Components

1. **Adaptive Critics**: Implement incremental approximations to dynamic programming
   - Compute an approximation of a strategic utility function
   - Guide adaptation of a controller that learns to take actions
   - Used for reinforcement learning of metacognitive behavior

2. **SHRUTI Network**: A connectionist solution for representing rules, variables, and dynamic bindings
   - Uses temporal synchrony for dynamic binding
   - Supports rapid inference for reflexive reasoning
   - Implements stories and argument structures as n-ary predicates and inferential links

3. **Situation Model**: Encompasses all information actively instantiated in the recognition model network
   - Includes observations, evidence, stories, and arguments
   - Can have many active and supported stories
   - Handles uncertainty and conflict

4. **Reflexive Reasoning**: Concerned with inferences made very quickly (within milliseconds)
   - Performed when incorporating new evidence
   - Done within story structures
   - Propagation of learned arguments is reflexive
   - Background knowledge constrains the flow of inference

5. **Deictic Representations**: Used to address dynamic binding problems
   - Dynamically bind key representational patterns into deictic markers
   - Interface the recognition model to the metacognitive system
   - Allow metacognition to focus on specific information patterns

### Processing Approach

The system considers one story at a time, emulating human behavior:
- Metacognition focuses on a particular story
- Generates assumptions whose implications are reflexively propagated
- Uses these to generate actions and expected value of outcomes
- Avoids making estimates of aggregate quantities
- Constrains search in a plausible way
- Reduces complexity of output representations

## Example: Implementation of Metacognitive Strategies

The paper illustrates the cyclical nature of critiquing and correcting with a critical incident from TADMUS interviews, involving an Anti-Air Warfare Coordinator (AAWC) evaluating a slow, non-responsive aircraft approaching a cruiser:

1. **Initial Conflict**: Slow speed conflicted with expectations of a hostile-intent story
2. **Assumption Generation**: AAWC assumed aircraft was looking for a target (but needed to specify how)
3. **First Hypothesis**: Aircraft searching visually (explains slow speed but is unreliable)
4. **Testing by Simulation**: If searching visually, it would fly erratically, but it was flying straight (conflict)
5. **Alternative Assumption**: Aircraft might have prior knowledge of target location
6. **Testing Again**: If it had precise intelligence, it would head toward the cruiser, but it wasn't (conflict)
7. **Return to Incompleteness**: Discard visual search assumption, need new localization method
8. **Second Hypothesis**: Aircraft searching electronically (also unreliable)
9. **Testing Again**: If searching electronically, it would be emitting, but it wasn't (conflict)
10. **Final Attempt**: Consider that aircraft might shoot without knowledge of target location (unreliable)
11. **Conclusion**: Failure to construct a plausible hostile intent story led to delayed engagement

The aircraft turned out to be friendly, validating the AAWC's cautious approach.

## Conclusions

The authors propose that:
1. Metacognitive behavior operates over recognitional models of causal relations and associated measures of uncertainty and conflict
2. Metacognitive skill is enhanced by domain knowledge
3. Information for the metacognitive system is filtered through a deictic representation controlled by dynamic attentional focus

### Implications

1. Metacognitive behavior is organized around a small, regular subset of structures in the recognitional system
2. Metacognitive skills, once acquired, may be transferred to new domains
3. There must be boundaries on recursive embedding of representations in intelligent systems
4. Some adaptive learning in the reflexive reasoning system is not possible without the parallel metacognitive system

The architecture divides cognitive behavior into recognitional processes (reflexive inference, action policies, expected utility) and metacognitive processes (monitoring, critiquing, correcting) to further the understanding and construction of adaptive intelligent agents.
