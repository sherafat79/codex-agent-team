---
name: codex-agent-team
description: Inspect any software repository and install or adapt a Codex multi-agent team to its actual language, frameworks, architecture, tooling, risks, and conventions. Use when the user asks to add a multi-agent structure, create project-specific custom agents under .codex/agents, convert role prompts into Agent Contracts, define orchestrator delegation rules, or port an existing agent setup from one stack (such as FastAPI or NestJS) to another (such as React, Next.js, Django, Spring, Go, or a monorepo).
---

# Codex Agent Team

Create the smallest useful project-specific agent team. Derive every stack-specific instruction from
repository evidence; never copy framework vocabulary, commands, paths, or risks from the source template.

## 1. Establish authority and target

- Resolve the target repository root.
- Treat an install/adapt request as authorization to edit only the target project's agent configuration
  and directly related workflow documentation.
- For an audit or proposal-only request, remain read-only.
- Read all applicable `AGENTS.md` files and referenced mandatory instructions before acting.
- Inspect scoped Git status/diffs and preserve unrelated or pre-existing changes.
- Use `apply_patch` for edits. Follow the repository's required shell prefix and package manager.

## 2. Build an evidence-backed project profile

Read [references/stack-adaptation.md](references/stack-adaptation.md) completely, then inspect the target.
Record evidence for:

- languages, frameworks, runtime versions, package managers, and lockfiles;
- application/deployable boundaries and architecture/layer conventions;
- API/UI/data/auth/upload/integration/infrastructure surfaces;
- build, lint, typecheck, test, migration, and deployment commands that actually exist;
- documentation sources of truth and rules for structural changes;
- current test/CI/container state, including explicit absence;
- existing `.codex/agents`, `.codex/config.toml`, `AGENTS.md`, and plan templates.

Do not infer a framework solely from a file extension. Do not claim tools or tests exist without manifest,
script, configuration, or source evidence. Follow local documentation-fetching rules when current library
or CLI syntax is required.

## 3. Select the minimal team

Always cover these six questions/jobs, but do not create redundant agents:

1. Explorer — **How does it work now?**
2. Architect — **How should we change it?**
3. One or more Workers — **Make the change.**
4. Test Engineer — **Did we break anything?**
5. Security Reviewer — **Did we create a security problem?**
6. Validator — **Did we actually satisfy the request?**

Choose worker names and scopes from the repository profile:

- use `frontend_worker` for a client-only UI application;
- use `backend_worker` for an API/service backend;
- use `fullstack_worker` for a tightly coupled full-stack application;
- use `mobile_worker`, `data_worker`, or `infra_worker` only when that is the primary implementation surface;
- use `implementation_worker` when no narrower name is evidence-backed;
- add a `fast_worker` only when recurring low-risk mechanical work has a useful, enforceable boundary;
- add another specialist only for a substantial independent deployable or recurring boundary. Mere
  non-triviality is not enough.

The root session remains the orchestrator; do not create an orchestrator agent file.

## 4. Generate Agent Contracts

Read [references/agent-contracts.md](references/agent-contracts.md) completely before writing prompts.
Create one TOML file per selected agent under `.codex/agents/`.

Every `developer_instructions` prompt must contain exactly these seven ordered sections:

1. `ROLE`
2. `OBJECTIVE`
3. `INPUTS`
4. `RESPONSIBILITIES`
5. `PERMISSIONS`
6. `STOP / ESCALATION CONDITIONS`
7. `OUTPUT SCHEMA`

Enforce these invariants:

- each agent answers only its assigned question/job;
- Explorer, Architect, Security Reviewer, and Validator are `read-only`;
- implementation workers are `workspace-write` but contractually restricted to explicit scoped ownership;
- Test Engineer is `workspace-write`, defaults to no tracked edits, and may edit tests only when the user
  explicitly requested test changes and the delegation owns those files;
- runtime/sandbox capability never expands contract permissions;
- every agent stops before acting if any handoff field is missing or contradictory;
- prompts name the target stack, real paths, real commands, architecture conventions, and real risks;
- prompts state absent capabilities instead of importing them from another project.

Reuse supported model names from existing local agent configuration when available. If support is not
evidenced, omit model-specific overrides and inherit the root model rather than inventing a model ID.

## 5. Install the orchestration workflow

Merge rather than overwrite existing project instructions.

- Add/update `.codex/config.toml` with an `[agents]` table. Default to `max_threads = 6` and
  `max_depth = 1` unless local constraints justify another bounded value. Preserve unrelated settings.
- Add/update `AGENTS.md` with:
  - root-direct-by-default multi-agent gate;
  - ordered role handoffs;
  - read-only and scoped-write role classification;
  - final Validator gate for multi-agent tasks;
  - safe parallelism and exclusive write ownership;
  - the delegation envelope below.
- Add/update `PLANS.md`, or the repository's canonical equivalent, with project-specific current-state,
  design, task ownership, acceptance, security, migration, docs, and conditional validation fields.
- Follow repository rules for structural documentation and indexes if this workflow change qualifies.

Require every delegation to contain:

- **INPUT** — user request and exact upstream evidence/decisions/results;
- **SCOPE** — behavior, paths, symbols, trust boundaries, responsibility, and exclusive write ownership;
- **CONSTRAINTS** — repository, compatibility, security, permission, environment, tooling, and exclusions;
- **EXPECTED OUTPUT** — the single question/job, output schema, evidence, checks, and verdict;
- **STOP CONDITIONS** — ambiguity, missing evidence, unsafe actions, conflicts, and task-specific blockers.

Make each handoff output the relevant next handoff's input. Preserve the original user request through
the final Validator handoff.

## 6. Remove source-template contamination

Search all generated/updated workflow files for terms from unrelated stacks. Replace copied concepts with
target evidence. Examples include NestJS/TypeORM/AdminJS/Yarn in a Python project or SQLModel/Alembic/uv
in a React-only project. Keep a term only when the target repository actually contains that surface.

Do not add tests, CI, containers, migrations, frontends, or dependencies merely because an agent template
mentions them.

## 7. Validate

Run the bundled validator after generation:

```text
python <skill-directory>/scripts/validate_agent_team.py --project <target-root>
```

Pass `--plan-file <relative-path>` when the repository uses a plan file other than `PLANS.md`. Pass one or
more `--forbid-term <term>` arguments for evidence-backed irrelevant source-stack terms.

Also run the repository's required scoped Git diff/status checks and a whitespace/diff check. Do not run
application tests, formatters, migrations, or services merely to validate agent configuration.

Fix every validator error and rerun until it passes.

## 8. Report

Report:

- detected project profile and selected team;
- created/updated workflow files;
- read-only vs scoped-write boundaries;
- validation commands and results;
- preserved existing settings/changes;
- assumptions, omitted roles, and any escalation.

Do not claim the team is installed when contract validation fails.
