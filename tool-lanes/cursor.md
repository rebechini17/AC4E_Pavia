# Tool Lane - Cursor

Use this lane if you want an IDE-first workflow.

## Setup

1. Install Cursor and sign in.
2. Open this repository folder.
3. Use Agent for implementation, Ask/read-only prompts for exploration, and Plan
   where your Cursor version exposes it.
4. Ask Cursor:

   ```text
   Read AGENTS.md and START_HERE.md. Do not edit files. What project guidance is active?
   ```

## Workshop Pattern

- Use `AGENTS.md` for shared project context.
- Add `.cursor/rules/` only when scoped rules help.
- Use bundled **SDD** skill (`.cursor/skills/sdd/`) and **sdd-orchestrator** (`.cursor/agents/sdd-orchestrator.md`) for the Day 2 spec workflow.
- Use Agent Skills and subagents if available in your version.
- Use Cloud Agents only for branch-isolated work that you will review.
- Review the diff and run tests before merging.

## Optional Cursor Rule

Create `.cursor/rules/economics-research.mdc` if you want scoped guidance:

```markdown
---
description: Economics research coding standards
globs: ["**/*.py", "**/*.md", "**/*.tex"]
---

- Use relative paths.
- Document data transformations, units, and sample restrictions.
- Do not edit data/raw or data/private.
- Run the documented verification command before claiming success.
```

## Verify In Your Version

Cursor UI labels for Agent, Plan, Cloud Agents, skills, hooks, and review surfaces
can change. Verify them before teaching from screenshots.
