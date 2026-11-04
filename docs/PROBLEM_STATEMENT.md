# LotLens — Persistent Failure Intelligence for Manufacturing

## Problem statement

Manufacturing organisations accumulate defect reports, supplier inspection records, production-batch information and corrective-action documentation. However, knowledge from previous investigations remains fragmented across reports, spreadsheets and individual engineering teams.

This makes it difficult to recognise recurring failures across suppliers, components and production batches; evaluate whether corrective actions were effective; and distinguish genuinely related failures from defects that merely share similar symptoms.

## Proposed solution

LotLens is a persistent-memory-powered manufacturing investigation agent. It connects structured manufacturing records with historical investigation experiences, remembers verified outcomes and unsuccessful corrective actions, identifies potentially recurring failure patterns, and recommends evidence-backed next investigative steps.

Hindsight is the required persistent-memory layer. The transactional database remains the source of truth for defect cases, evidence, actions and QA verification. An LLM helps interpret retrieved evidence and produce structured recommendations. Engineers retain decision-making authority; LotLens does not autonomously declare physical root causes or close cases.

## Core workflow

1. An engineer records a defect, supplier, component, production lot, symptoms and available evidence.
2. LotLens retrieves relevant historical experiences.
3. The system validates referenced historical cases against structured records.
4. The agent compares similarities, differences, prior corrective actions and verified outcomes.
5. It proposes investigation steps and candidate explanations with traceable supporting evidence and uncertainty.
6. An engineer reviews the recommendation and records the action taken.
7. QA verifies the result.
8. The verified outcome is retained as a new experience for future investigations.

## MVP boundaries

### In scope
- Defect investigation intake and case history.
- Supplier, component and production-lot relationships.
- Hindsight retain, recall and reflect proof of concept.
- Evidence-backed investigation recommendations.
- Corrective-action tracking.
- Human/QA verification and outcome retention.
- Audit trail, basic roles and automated tests.

### Out of scope for the first release
- ERP/MES integrations.
- Factory IoT and live sensor ingestion.
- Autonomous production shutdown or supplier communication.
- Automatic root-cause certification.
- Predictive maintenance platform.
- Complex multi-tenant enterprise administration unless required by the event.

## Safety and correctness principles
- Similar symptoms do not prove a shared root cause.
- Historical facts, hypotheses and recommendations must be labelled separately.
- Every historical claim must link to a real case/evidence record.
- Unverified outcomes must not be represented as confirmed learning.
- QA approval is required before a case is marked verified/closed.
- Hindsight outage must not corrupt transactional case records.
- The agent must report insufficient or conflicting evidence instead of inventing certainty.

## Primary demo hypothesis

Given a new BMS connector failure, LotLens should retrieve relevant historical incidents, distinguish a superficially similar case with a different cause, surface an earlier corrective action that did not prevent recurrence, and propose a targeted next investigation. A human verifies the eventual outcome, and the new verified experience becomes available to later investigations.

All initial manufacturing data must be clearly labelled synthetic unless sourced and authorised for use.

## Hackathon alignment

The project is designed to demonstrate innovation, central use of Hindsight memory, technical implementation, user experience and real-world relevance. The key demonstration is a meaningful before/after comparison showing how accumulated and verified memory changes the investigation—not a generic chatbot response.
