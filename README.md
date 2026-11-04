# LotLens

**Persistent Failure Intelligence for Manufacturing**

LotLens is a proposed Hindsight-powered manufacturing investigation agent. It helps quality engineers connect historical defect experiences, remember verified and unsuccessful corrective actions, and formulate evidence-backed next investigations.

> Status: project kickoff / architecture review. Implementation and Hindsight integration are not yet complete.

## Start here
- [Problem statement](docs/PROBLEM_STATEMENT.md)
- [Requirements and MVP](docs/REQUIREMENTS.md)
- [Architecture decision brief](docs/ARCHITECTURE.md)
- [Six-role engineering board](docs/ENGINEERING_BOARD.md)
- [Hindsight memory design](docs/MEMORY_DESIGN.md)
- [Draft API contracts](docs/API_CONTRACTS.md)
- [QA strategy](docs/QA_STRATEGY.md)
- [Testing strategy](docs/TESTING_STRATEGY.md)

## Core principle
The transactional database is the source of truth for cases and verification. Hindsight stores derived investigation experiences. LLM outputs are untrusted until validated. Humans approve actions and QA verifies outcomes.

## Current phase
Architecture and feasibility review. Do not assume a runtime stack, create production secrets, or claim a live deployment until the engineering board approves decisions and the Hindsight proof of concept passes.
