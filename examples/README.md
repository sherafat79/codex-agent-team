# Executable examples

These are complete, validator-ready agent-team installations rather than documentation snippets.

| Fixture | Input | Generated team |
| --- | --- | --- |
| [`root-only-typo`](root-only-typo/README.md) | Fix a documentation typo | Root only |
| [`jwt-refresh`](jwt-refresh/README.md) | Add JWT refresh token support | Explorer, Architect, Backend Worker, Security Reviewer, Validator |

From the repository root:

```bash
python skills/codex-agent-team/scripts/validate_agent_team.py --project examples/root-only-typo
python skills/codex-agent-team/scripts/validate_agent_team.py --project examples/jwt-refresh
```
