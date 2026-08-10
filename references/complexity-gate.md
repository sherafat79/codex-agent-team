# Complexity Gate

Root handles work directly by default. Multi-agent execution is justified only when bounded independent
work or review produces enough safety or clarity to outweigh coordination cost.

## Decision-support signals

Add the relevant signals; do not treat the total as an automatic verdict.

| Signal | Weight |
| --- | ---: |
| Cross-module change | +2 |
| Authentication or authorization | +2 |
| Database schema or migration | +2 |
| Infrastructure or deployment | +2 |
| External integration | +1 |
| More than about five likely affected files | +1 |
| Ambiguous behavior | +1 |
| Multiple deployables/services | +1 |
| Sensitive data handling | +1 |
| Networking change | +1 |

Suggested interpretation:

- `0-2`: root normally handles exploration, implementation, and validation directly.
- `3-4`: Explorer, an implementation worker, and independent validation may be enough.
- `5-7`: consider Explorer, Architect, implementation, regression assessment, and Validator.
- `8+`: consider the full applicable workflow, including Security Reviewer.

Record the observed signals and the root's judgment, not only the number.

## Overrides

Use independent security review regardless of score when a change can affect authentication,
authorization, secrets, tenant/ownership enforcement, sensitive data, executable input, uploads,
network exposure, infrastructure permissions, or a high-impact external integration. Require regression
assessment for high-blast-radius behavior or a risky compatibility boundary even when the file count is
small. Require architecture review when product behavior, migration, or cross-service ownership cannot be
implemented safely from existing patterns.

Conversely, a high score caused by repetitive independent edits does not require every specialist. Root
may collapse capabilities when the decision is mechanical, evidence is clear, and review would not be
independent or useful. Explicit user requests for multi-agent execution open the gate but do not justify
irrelevant agents or broader permissions.

## Centralized execution

Root alone selects agents, sequences dependencies, resolves escalations, and authorizes new work. Keep
`max_depth = 1`. `max_threads` controls capacity, not desired concurrency; any positive value is valid.
Parallelize only non-overlapping work with no evidence or decision dependency. Exploration -> architecture
-> implementation -> review -> validation remains sequential even when threads are available.

