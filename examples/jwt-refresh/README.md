# JWT refresh-token fixture

**Input:** `Add JWT refresh token support.`

**Output:** Explorer -> Architect -> Backend Worker -> Security Reviewer -> Validator.

The profile records an authenticated HTTP API with persistent token state. Authentication is high risk
and data is medium risk, so security review is active; regression assessment stays conditional because it
can be owned by root unless the final diff expands the compatibility surface.

Validate from the repository root:

```bash
python scripts/validate_agent_team.py --project examples/jwt-refresh
```
