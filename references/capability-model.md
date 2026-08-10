# Capability and Project Profile Model

Select agents from evidence-backed capabilities and risk, not from framework names or a fixed role count.

## Decision pipeline

```text
Repository evidence
  -> Project profile
  -> Capability map
  -> Risk profile
  -> Smallest useful team
  -> Agent Contracts
```

`Capability != Agent`. A capability describes work that must be covered; an agent is only one possible
owner. Root may safely cover several capabilities on a small task.

## Lightweight profile

Generate `.codex/agent-team.toml` using only verified facts:

```toml
version = 1

[project]
type = "library"
evidence = ["pyproject.toml", "src/package/__init__.py"]

[stack]
languages = ["Python"]
frameworks = []
package_manager = "uv"
deployment = []

[features]
http_api = false
persistence = false
authentication = false
authorization = false
uploads = false
external_integrations = false
background_jobs = false
networking = false
infrastructure = false

[risk]
authentication = "low"
data = "low"
infrastructure = "low"
external_integration = "low"

[capabilities.exploration]
mode = "root"
justification = "The manifest and one entrypoint bound the change."

[capabilities.implementation]
mode = "agent"
agent = "implementation_worker"

[capabilities.validation]
mode = "agent"
agent = "validator"

[capabilities.architecture]
mode = "conditional"
justification = "Activate only for cross-module design decisions."

[capabilities.regression_assessment]
mode = "root"
justification = "The root can run the single focused check."

[capabilities.security_review]
mode = "not_applicable"
justification = "No trust boundary or sensitive surface is present."
```

Allowed project types are `backend`, `frontend`, `fullstack`, `library`, `infrastructure`, `monorepo`,
and `other`. Keep `languages` and `frameworks` as evidence-backed lists. Omit optional stack facts that are
unknown rather than inventing a value. All feature flags must be explicit booleans. Risk values are
`low`, `medium`, or `high`.

## Capability modes

| Mode | Meaning | Required evidence |
| --- | --- | --- |
| `root` | Root owns the capability for this installation/task class. | Why separate delegation adds no safety. |
| `agent` | A generated dedicated contract owns it. | Existing agent name with the matching objective. |
| `existing_specialist` | An already-present compatible contract owns it. | Existing agent name and matching objective. |
| `conditional` | Activate only when named task/risk conditions occur. | Concrete activation conditions. |
| `not_applicable` | The repository/task has no relevant surface. | Evidence-backed reason. |

Exploration, implementation, and validation are always required and therefore use `root`, `agent`, or
`existing_specialist`. Architecture, regression assessment, and security review are conditional and may
use any mode. A conditional capability becomes root- or agent-owned when its activation condition is met.

## Selection rules

1. Determine capabilities from behavior and trust boundaries, not framework labels.
2. Apply complexity and risk signals to the current task.
3. Reuse compatible specialists before creating another contract.
4. Assign root when delegation would add coordination without independent evidence or safety.
5. Create an agent only when its bounded question/job materially helps.
6. Record why conditional/not-applicable decisions are safe.

Example: framework detection alone does not justify a backend worker or security reviewer. Verified auth,
persistence, and external integration surfaces may justify implementation and security capabilities;
cross-module behavior may separately activate architecture review.

## Contradictions

Reject maps where a required capability is conditional/not applicable, an agent mode has no agent, a root
mode also names an agent, a named contract answers the wrong question, or a conditional/not-applicable
mode lacks justification. Risk scores guide selection but never silently invent a capability.
