# ADR-0001: Separate canonical records from persistent agent memory

- Status: Proposed
- Date: 2026-11-04

## Context
LotLens must use Hindsight centrally while keeping manufacturing case status, verification and evidence auditable and deterministic.

## Decision
The transactional database is the canonical source for cases, evidence, corrective actions and QA verification. Hindsight stores derived investigation experiences used for recall and reflection. LLM outputs cannot directly mutate case state.

## Consequences
- Every memory reference must resolve to a canonical case/evidence record before being shown.
- Memory sync occurs after successful transactional commit and needs retry/reconciliation.
- Stale or conflicting memories must be checked against canonical records.
- Hindsight failure must not corrupt case data.
- Memory payload schema and organisation scope require explicit review before implementation.

## Open questions
- Exact Hindsight bank and metadata strategy.
- Versioned experience schema.
- Idempotency mechanism and sync status model.
- Data minimisation and retention policy.
