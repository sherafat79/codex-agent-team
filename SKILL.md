---
name: codex-agent-team
description: Inspect any software repository and install or adapt the smallest capability-driven Codex agent team for its actual architecture, tooling, task complexity, and risks. Use when the user asks to add project-specific agents under .codex/agents, define Agent Contracts and root-owned orchestration, or port an existing agent setup between stacks.
---

# Codex Agent Team

Build the smallest useful project-specific agent team. Derive every stack-specific instruction from
repository evidence. A required capability does not imply a dedicated agent.

## 1. Establish authority and target

- Resolve the target repository root.
- Treat an install/adapt request as authorization to edit only the target project's agent configuration
  and directly related workflow documentation.
- For an audit or proposal-only request, remain read-only.
- Read all applicable `AGENTS.md` files and mandatory referenced instructions.
- Inspect scoped Git status/diffs and preserve unrelated or pre-existing changes.
- Use `apply_patch` for edits and follow the repository's required shell prefix and package manager.

## 2. Build the project profile

Read [references/stack-adaptation.md](references/stack-adaptation.md) and
[references/capability-model.md](references/capability-model.md) completely before generation. Inspect
only enough evidence to record:

- project type, languages, frameworks, runtimes, package manager, and lockfiles;
- deployables, entrypoints, architecture/layers, and control/data flow;
- HTTP, persistence, auth, uploads, jobs, network, integrations, and infrastructure surfaces;
- build, lint, typecheck, test, migration, and deployment commands that actually exist;
- risk levels for auth, data, infrastructure, and external integrations;
- current docs, tests, CI, containers, agents, config, and explicit absences;
- exact source paths supporting every material conclusion.

Write the lightweight profile and capability map to `.codex/agent-team.toml`. Do not infer a capability
from a framework name alone. The required decision pipeline is:

```text
Repository evidence -> Project profile -> Capability map -> Risk profile -> Team selection -> Contracts
```

Do not continue while a material ambiguity could change the team or a trust boundary.

## 3. Apply the complexity gate

Read [references/complexity-gate.md](references/complexity-gate.md) completely. Root handles simple work
directly. Use the score only as decision support and record the signals, overrides, and judgment that
opened or closed the multi-agent gate. Security-sensitive or irreversible work may require independent
review regardless of score.

## 4. Map capabilities to the smallest team

Always cover these capabilities, but allow root coverage:

- `exploration` — **How does it work now?**
- `implementation` — **Make the change.**
- `validation` — **Did we actually satisfy the request?**

Evaluate these conditionally:

- `architecture` — **How should we change it?**
- `regression_assessment` — **Did we break anything?**
- `security_review` — **Did we create a security problem?**

For each capability, set one mode in `.codex/agent-team.toml`: `root`, `agent`,
`existing_specialist`, `conditional`, or `not_applicable`. Root, conditional, and not-applicable modes
require a concrete justification. Always-required capabilities cannot remain conditional or be not
applicable. Agent modes must name an installed contract that answers the corresponding question/job.

Choose the narrowest evidence-backed implementation worker: `frontend_worker`, `backend_worker`,
`fullstack_worker`, `mobile_worker`, `data_worker`, `infra_worker`, or `implementation_worker`. Add
separate workers only for substantial independent ownership boundaries.

Add `mechanical_worker` only for recurring deterministic edits with a safe enforceable boundary. It may
perform explicit renames, repetitive metadata/field edits, constant/config changes, obvious file moves,
and other straightforward low-risk changes. It must not make architecture, security, data-model, auth,
migration, networking, infrastructure, or integration decisions. Those conditions require escalation to
root. `fast_worker` is deprecated; migrate it rather than generating it.

The root session is the only orchestrator. Never create an orchestrator contract, recursive hierarchy,
or autonomous subagent chain.

## 5. Generate Agent Contracts

Read [references/agent-contracts.md](references/agent-contracts.md) and
[references/handoff-protocol.md](references/handoff-protocol.md) completely before writing prompts.
Create contracts only for capabilities assigned to agents, under `.codex/agents/`.

Every `developer_instructions` prompt must contain exactly these seven ordered sections:

1. `ROLE`
2. `OBJECTIVE`
3. `INPUTS`
4. `RESPONSIBILITIES`
5. `PERMISSIONS`
6. `STOP / ESCALATION CONDITIONS`
7. `OUTPUT`

Enforce these invariants:

- each agent answers only its assigned question/job and uses the smallest safe scope;
- Explorer, Architect, Security Reviewer, and Validator are `read-only`;
- implementation workers are `workspace-write` only within exact assigned paths/files;
- Test Engineer is `workspace-write`, defaults to no tracked edits, and may edit tests only when the user
  or project policy requires them and the delegation owns the exact files;
- runtime/sandbox capability never expands contract permission;
- every agent stops before acting on missing, ambiguous, contradictory, unsafe, or out-of-scope input;
- prompts use the target's real paths, terms, commands, architecture, and risks;
- absent capabilities stay absent instead of being scaffolded.

Prefer `SMALLEST SAFE DIFF`: no unrelated refactors, opportunistic cleanup, unapproved dependencies,
migrations, public API changes, production data changes, or weakened checks.

## 6. Install root-owned orchestration

Merge rather than overwrite existing instructions.

- Add/update `.codex/config.toml`. Default to `max_threads = 4` and require `max_depth = 1`. Any positive
  `max_threads` is valid, including `1` for deliberate sequential execution.
- Add/update `.codex/agent-team.toml` with the evidence-backed profile, risks, and capability modes.
- Add/update `AGENTS.md` with the root-direct gate, capability mapping, role permissions, ordered
  dependencies, conservative parallelism, exclusive write ownership, escalation, and handoff protocol.
- Add/update `PLANS.md`, or its canonical equivalent, with current state, decisions, task ownership,
  acceptance, security, migration, docs, checks, and traceability fields.
- Follow repository rules for structural documentation and indexes.

Parallelize only truly independent workstreams. Exploration may inform architecture; architecture informs
implementation; implementation informs regression/security review; those dependencies stay sequential.
Any work discovered by a subagent returns to root for a new decision and delegation.

Use **Independent Review / Context Isolation**: Architect receives Explorer facts and uncertainties, not
speculation; Worker receives approved decisions and scope; reviewers receive the relevant diff and
objective evidence, not optimistic conclusions. Validator receives the original request, constraints,
acceptance criteria, final diff, test results, and security findings.

Use lightweight trace IDs for non-trivial work: `E#` evidence, `D#` decisions, `W#` tasks/changed files,
`T#` test evidence, `S#` security evidence, and `R#` requirements. Preserve the original user request
through the final validation handoff.

## 7. Remove source-template contamination

Search generated workflow files for unrelated frameworks, paths, commands, integrations, and legacy
`fast_worker` references. Keep a specific term only when target evidence or the request supports it. Do
not add tests, CI, containers, migrations, frontends, dependencies, or agents merely because a template
mentions them.

## 8. Validate

Run the dependency-free validator after generation:

```text
python <skill-directory>/scripts/validate_agent_team.py --project <target-root>
```

Pass `--plan-file <relative-path>` for a different plan file and repeat `--forbid-term <term>` for
evidence-backed contamination terms. Also run scoped Git status/diff and a whitespace check. Do not run
application services, migrations, formatters, or broad test suites merely to validate agent configuration.
Fix every validator error and rerun until it passes.

## 9. Report

Report the profile and evidence, capability modes and selected agents, read-only/scoped-write boundaries,
files changed, validation commands/results, preserved changes, compatibility notes, omissions, and any
escalation. Do not claim installation succeeded when validation fails.
