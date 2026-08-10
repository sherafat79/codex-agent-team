# Root-only typo fixture

**Input:** `Fix a typo in the documentation.`

**Output:** Root handles exploration, implementation, and validation directly. No Agent Contracts are
generated because delegation would add coordination without useful independent evidence or safety.

Validate from the repository root:

```bash
python scripts/validate_agent_team.py --project examples/root-only-typo
```
