# Stack and Architecture Adaptation

Use repository evidence to build a project profile before mapping capabilities or selecting agents.

## Evidence order

Prefer evidence in this order:

1. Repository instructions and indexed architecture documentation.
2. Lockfiles, manifests, workspace definitions, and tool configuration.
3. Entrypoints, directory boundaries, imports, and runtime wiring.
4. Existing scripts, CI, deployment, migration, and test configuration.
5. README claims confirmed by current files.

Record exact paths for material conclusions. Mark conflicting or stale documentation. Do not perform broad
scans when a manifest and a few entrypoints answer the question.

## Discovery checklist

- instructions: `AGENTS.md`, referenced rules, architecture/design docs;
- JavaScript/TypeScript: manifests, lockfiles, workspace files, `tsconfig*`, framework/build config;
- Python: `pyproject.toml`, lockfiles/requirements, framework config, entrypoints;
- Java/Kotlin: Maven/Gradle files, application configuration, startup sources;
- Go/Rust/.NET: manifests/workspaces/solutions and executable entrypoints;
- mobile: Expo/EAS, React Native, Android Gradle, Xcode project/workspace evidence;
- data: models, migrations, database config, query/session/transaction layers;
- delivery: CI workflows, containers, Kubernetes, Terraform, hosting configuration;
- quality: actual build/lint/typecheck/test scripts and configurations;
- existing agent setup: `.codex/agents/*.toml`, `.codex/config.toml`, `.codex/agent-team.toml`, workflow
  instructions, and plan templates.

## Project profile

Record this evidence-backed internal profile, then serialize the stable facts to the lightweight
`.codex/agent-team.toml` format in [capability-model.md](capability-model.md):

```text
ROOT:
PROJECT TYPE: backend | frontend | fullstack | library | infrastructure | monorepo | other
LANGUAGES / VERSIONS:
FRAMEWORKS / VERSIONS:
PACKAGE MANAGER / LOCKFILE:
DEPLOYABLES:
ARCHITECTURE / LAYERS:
ENTRYPOINTS / CONTROL-DATA FLOW:
HTTP API:
PERSISTENCE / MIGRATIONS:
AUTHENTICATION / AUTHORIZATION:
UPLOADS / FILESYSTEM:
BACKGROUND JOBS:
NETWORKING:
EXTERNAL INTEGRATIONS:
INFRASTRUCTURE:
BUILD / LINT / TYPECHECK:
TESTS:
CI / DEPLOYMENT / CONTAINERS:
STRUCTURAL DOC RULES:
EXISTING AGENT SETUP:
KNOWN ABSENCES:
RISK: auth, data, infrastructure, external integration
SOURCE-TEMPLATE TERMS TO FORBID:
EVIDENCE: exact paths/symbols
```

Do not continue while a material field is ambiguous enough to change capability coverage, worker scope,
or a trust boundary. Do not confuse “not found in bounded inspection” with “does not exist.”

## From profile to capabilities

Framework names are supporting evidence, never the decision. First identify behavior and risk, then decide
whether root or an agent should own each capability.

Bad:

```text
NestJS -> backend_worker + security_reviewer
```

Better:

```text
HTTP controllers + auth guards + persistence + external callback verified
-> backend implementation capability
-> security review activated for changed trust boundary
-> architecture review only if the change crosses modules/contracts
```

## Implementation worker selection

Choose the narrowest primary worker that owns the normal implementation path:

| Evidence-backed project shape | Default worker | Typical scope |
| --- | --- | --- |
| React/Vite/SPA/client-only | `frontend_worker` | components, hooks, state, routing, accessibility, client adapters |
| Tightly coupled web app | `fullstack_worker` | server routes/actions, UI, shared contracts, present persistence |
| API/service backend | `backend_worker` | handlers, validation, services, present persistence/auth/integrations |
| Expo/React Native/native app | `mobile_worker` | navigation, native UI, device APIs, scoped build config |
| ETL/analytics/ML pipeline | `data_worker` | pipelines, schemas, transformations, data validation |
| Terraform/Kubernetes/platform repo | `infra_worker` | infrastructure code, delivery, secrets boundaries, rollout |
| Library/CLI/unclear single surface | `implementation_worker` | project-native source, CLI, validation, packaging |

For a monorepo, create separate workers only when deployables have independent tooling and exclusive
ownership and the complexity gate benefits. Otherwise use one worker with explicit per-task scope.

Add `mechanical_worker` only for explicit deterministic edits. It cannot own auth/authorization, secrets,
data/schema/query/migration, uploads/filesystem/networking, public API/validation behavior, domain-critical
rules, concurrency, infrastructure, deployment, or integrations. It stops when architecture, security,
data-model, or unspecified behavioral judgment appears.

## Contract vocabulary

Use repository-native terms rather than importing an idealized layer:

| Concern | Adapt from evidence |
| --- | --- |
| UI | component model, router, state/data fetching, styling, accessibility, build tool |
| API | route/controller/handler model, validation types, middleware/dependencies/guards |
| Business logic | services/use cases/domain modules that actually exist |
| Data | actual ORM/query library, session/transaction model, migrations, model registration |
| Auth | actual session/token/provider, enforcement points, roles/ownership |
| Tests | present framework, commands, environments, or explicit absence |
| Tooling | exact package manager and manifest scripts |
| Docs | canonical files and structural documentation rules |
| Deployment | only providers/files that exist or are explicitly requested |

## Risk adaptation

Security and validation focus on the changed attack surface:

- client UI: XSS, unsafe HTML, token storage, exposed secrets, redirects, supply chain;
- backend: authn/authz, IDOR, injection, mass assignment, validation, sensitive responses;
- data/migrations: transactionality, destructive changes, compatibility, rollback, tenant filters;
- uploads: size/type/path validation, exposure, malware handling, storage permissions;
- infrastructure: IAM, secrets, network exposure, state safety, rollout/rollback, CI credentials;
- integrations: SSRF, signature verification, retries/idempotency, credentials, untrusted responses.

## Contamination review

Before completion, search generated files for unrelated stacks, paths, commands, integrations, and legacy
role names. Confirm every surviving specific term is evidenced; absent capabilities remain absent; worker
responsibilities match the current architecture; and no test, CI, container, migration, dependency, or
agent was added merely because a template mentioned it.
