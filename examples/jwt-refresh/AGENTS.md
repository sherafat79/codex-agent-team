# JWT refresh orchestration

The Root Orchestrator sequences Explorer -> Architect -> Backend Worker -> Security Reviewer -> Validator.
Root keeps `max_depth = 1`, passes objective evidence rather than prior approval language, and assigns
exclusive write ownership to the Backend Worker. Read-only agents report findings and never fix them.

Every handoff must contain:

- OBJECTIVE
- SCOPE
- INPUT EVIDENCE
- REQUIRED BEHAVIOR
- CONSTRAINTS
- MUST PRESERVE
- MUST NOT CHANGE
- ACCEPTANCE CRITERIA
- ESCALATION CONDITIONS
- EXPECTED OUTPUT
