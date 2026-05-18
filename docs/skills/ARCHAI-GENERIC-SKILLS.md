# ArchAI Generic Skills Library

Use these skills automatically based on task. Format: `ARCHAI:skill-name`.

## Core Skills
- **think-before-architecting**: State assumptions, present 2-3 alternatives with trade-offs, ask clarifying questions if ambiguous. Surface risks explicitly.
- **reuse-first-analysis**: Before proposing new components, query knowledge base for existing patterns, assets, or decisions. Score reuse opportunity.
- **tradeoff-matrix**: Always produce a scored matrix (criteria: Cost, Performance, Security, Maintainability, Compliance, Time-to-Value). Quantify where possible.
- **structured-hld-lld**: Output in fixed JSON schema + C4/Mermaid diagrams. Include ADR-style decision records.
- **compliance-enforcement**: Cross-check against TOGAF, Well-Architected Frameworks, org policies, security standards. Flag violations with severity.
- **goal-driven-verification**: Define verifiable success criteria (e.g., "All non-functional reqs addressed + diagrams valid"). Loop via Reviewer agent until met.
- **surgical-documentation**: Edit only relevant sections. Preserve existing traceability and style.
- **subagent-orchestration**: Dispatch to specialized agents (Knowledge, Trade-off, Reviewer) with narrow scope + context.

**Meta Skills**:
- **writing-archai-skills**: Create new skills following this template (When to use, Steps, Examples, Guardrails).
- **verification-before-signoff**: Run full checklist + confidence score before presenting to user.

Reference these in every multi-turn EA task.
