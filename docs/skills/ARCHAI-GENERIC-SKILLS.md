---
title: ArchAI Generic Skills
category: Skills
version: 1.1
---

# ArchAI Generic Skills Library

Use these skills automatically based on task. Format: `ARCHAI:skill-name`.

## Core Architectural Skills
- **think-before-architecting**: State assumptions, present 2-3 alternatives with trade-offs, ask clarifying questions if ambiguous. Surface risks explicitly.
- **reuse-first-analysis**: Before proposing new components, query knowledge base for existing patterns, assets, or decisions. Score reuse opportunity.
- **tradeoff-matrix**: Always produce a scored matrix (criteria: Cost, Performance, Security, Maintainability, Compliance, Time-to-Value). Quantify where possible.
- **structured-hld-lld**: Output in fixed JSON schema + C4/Mermaid diagrams. Include Architecture Decision Records (ADRs).
- **compliance-enforcement**: Cross-check against TOGAF, Well-Architected Frameworks, org policies, security standards. Flag violations with severity.
- **goal-driven-verification**: Define verifiable success criteria. Loop via Reviewer agent until all criteria are met.
- **surgical-documentation**: Edit only relevant sections. Preserve existing traceability, versioning, and style.
- **subagent-orchestration**: Dispatch to specialized agents (Knowledge, Trade-off, Reviewer) with narrow scope and context.

## Advanced Architectural Skills
- **c4-modeling-depth**: Generate Context (L1), Container (L2), and Component (L3) diagrams with consistent labeling and standard notation.
- **tco-estimation**: Estimate Total Cost of Ownership including licensing, egress, compute, and maintenance.
- **migration-path-design**: Define 6R strategies (Rehost, Replatform, Refactor, Retire, Retain, Relocate) for legacy transitions.
- **zero-trust-validation**: Verify identity-based perimeter and least-privilege access for all interfaces and data flows.

## Meta & Continuous Improvement Skills
- **writing-archai-skills**: Create new skills following the standard template (When to use, Steps, Examples, Guardrails).
- **verification-before-signoff**: Run full automated checklist and confidence score before presenting final artifacts to user.

Reference these skills in every multi-turn EA task to ensure consistency and quality.
