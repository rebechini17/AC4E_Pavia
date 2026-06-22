# Topic 2 Reading - Research Pipeline and Spec-Driven Development

Spec-driven development helps keep research coding grounded in the research
question. It separates intent, requirements, design, and tasks so the agent does
not jump from a vague idea to a sprawling code edit.

## Reading Order (Day 2 Morning)

1. **Agent Skills** — what `SKILL.md` files are, how to attach/invoke a skill, and project vs user scope (see your tool lane doc).
2. **SDD via `/sdd`** — use the instructor SDD skill to scaffold `spec/` (or linked memo sections) before Sprint A.
3. **EARS and artifacts** — tables below; apply during the research design sprint.

## SDD For Research

| Stage | Research artifact |
| --- | --- |
| Intent | research question, contribution, audience, success criteria |
| Requirements | data contracts, output formats, numerical tolerances, replication needs |
| Design | data flow, estimator/model, robustness plan, folder map |
| Tasks | issues with acceptance criteria and verification |

## SDD Skill Layout (`spec/`)

After `/sdd init` (or equivalent), expect:

| File | Purpose |
| --- | --- |
| `spec/intent.md` | research question, audience, success criteria |
| `spec/requirements.md` | EARS-style REQ-* statements |
| `spec/design.md` | data flow, estimators, folder map |
| `spec/tasks.md` | ordered work units linked to requirements |
| `steering/coding-standards.md` | repo conventions for the agent |

Link or summarize these from `docs/research_design_memo.md` when the spec grows large.

## EARS Acceptance Criteria

Use concrete forms:

- WHEN a clean run starts, the pipeline SHALL exit 0.
- GIVEN fixed inputs, the script SHALL produce the same table values.
- IF a data source is unavailable, the repo SHALL document the blocker.

## Artifact Checklist

- `docs/research_design_memo.md`
- `docs/data_source_map.md`
- `references/bibliography.bib`
- backlog issues with acceptance criteria
- `notes/context_patterns.md`
