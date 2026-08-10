# Handoff Protocol

Every agent delegation is a deterministic contract owned by the root orchestrator. Do not delegate with
open-ended prompts such as “take a look and handle it.”

## Required fields

```text
OBJECTIVE
SCOPE
INPUT EVIDENCE
REQUIRED BEHAVIOR
CONSTRAINTS
MUST PRESERVE
MUST NOT CHANGE
ACCEPTANCE CRITERIA
ESCALATION CONDITIONS
EXPECTED OUTPUT
```

- **OBJECTIVE**: one question/job only.
- **SCOPE**: behavior, paths, symbols, trust boundaries, responsibility, and exclusive write ownership.
- **INPUT EVIDENCE**: exact upstream facts/results and trace IDs; distinguish fact from uncertainty.
- **REQUIRED BEHAVIOR**: observable outcomes in priority order.
- **CONSTRAINTS**: repository, compatibility, security, permission, environment, and tooling limits.
- **MUST PRESERVE**: existing contracts and behavior that cannot regress.
- **MUST NOT CHANGE**: explicit exclusions, unrelated modules, and forbidden external state.
- **ACCEPTANCE CRITERIA**: objective pass/fail conditions.
- **ESCALATION CONDITIONS**: ambiguity, missing evidence, unsafe actions, conflicts, and discovered scope.
- **EXPECTED OUTPUT**: role-specific schema, evidence, checks, changed files, findings, and verdict.

An agent stops before acting when a required field is missing, ambiguous, or contradictory. Additional work
returns to root; agents do not delegate it onward.

## Example implementation handoff

```text
OBJECTIVE
W1: Add the approved normalization behavior.

SCOPE
Own src/module-a/* and src/module-b/service.py only.

INPUT EVIDENCE
E1 current entrypoint; E3 current validation rule; D1 approved behavior.

REQUIRED BEHAVIOR
1. Normalize before persistence.
2. Preserve existing error mapping.

CONSTRAINTS
Use existing standard-library helpers and repository commands.

MUST PRESERVE
Public API compatibility and the current transaction boundary.

MUST NOT CHANGE
Unrelated module C, dependencies, or production data.

ACCEPTANCE CRITERIA
Focused scenarios pass and invalid input retains its current response.

ESCALATION CONDITIONS
Stop if a migration is necessary or behavior conflicts with authorization.

EXPECTED OUTPUT
Status, changed files, checks, deviations, remaining risks, and escalation.
```

## Traceability

For trivial tasks, paths and check results may be enough. For complex/high-risk tasks use lightweight IDs:

```text
R1 requirement -> E1 evidence -> D1 decision -> W1 task/files -> T1/S1 review -> V1 verdict
```

Do not create a separate tracking system. Keep IDs in the plan and handoffs where they reduce ambiguity.

## Independent Review / Context Isolation

Pass the minimum objective context needed for each question:

- Architect receives Explorer facts, conflicts, and uncertainty—not persuasive design speculation.
- Worker receives approved decisions, exact scope, constraints, and acceptance criteria—not unrelated
  exploration narrative.
- Test Engineer receives changed behavior, final diff, and criteria—not a claim that tests should pass.
- Security Reviewer receives the relevant diff, trust boundaries, and risk profile—not optimistic worker
  conclusions.
- Validator receives the original request, repository constraints, acceptance criteria, final diff, test
  evidence, and security findings—not other agents' approval language.

Independent reviewers inspect objective evidence and never “quickly fix” findings. Findings return to root
for a new scoped worker handoff.
