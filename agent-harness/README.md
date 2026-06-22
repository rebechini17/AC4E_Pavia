# Agent Harness

This folder contains portable agent assets:

- `skills/replication-checker/SKILL.md`
- `skills/sdd/SKILL.md` (templates in `skills/sdd/templates/`)
- `subagents/pr-reviewer.md`
- `subagents/sdd-orchestrator.md`
- `autonomous_agent_risk_card.md`

Copy these into tool-native locations only after reading them:

| Tool | Skill path | Agent/subagent path |
| --- | --- | --- |
| Codex | `.agents/skills/<name>/SKILL.md` or current documented path | tool-native subagent/custom agent config or explicit role prompt |
| Claude Code | `.claude/skills/<name>/SKILL.md` | `.claude/agents/<name>.md` |
| Cursor | `.cursor/skills/<name>/SKILL.md` | `.cursor/agents/<name>.md` |
