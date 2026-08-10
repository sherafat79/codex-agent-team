# Stack and Architecture Adaptation

Use repository evidence to build a project profile before choosing or writing agents.

## Contents

- Evidence order
- Discovery checklist
- Project profile schema
- Worker selection
- Contract vocabulary adaptation
- Risk adaptation
- Contamination review

## Evidence order

Prefer evidence in this order:

1. Repository instructions and indexed architecture documentation
2. Lockfiles, manifests, workspace definitions, and tool configuration
3. Entrypoints, directory boundaries, imports, and runtime wiring
4. Existing scripts, CI, deployment, migration, and test configuration
5. README claims only when confirmed by current files

Record exact paths for every material conclusion. Mark conflicting or stale documentation explicitly.

## Discovery checklist

Inspect only relevant files, using targeted search/listing:

- instructions: `AGENTS.md`, referenced rules, architecture/design docs;
- JavaScript/TypeScript: `package.json`, lockfiles, workspace files, `tsconfig*`, framework/build config;
- Python: `pyproject.toml`, `uv.lock`, requirements files, framework config, entrypoints;
- Java/Kotlin: `pom.xml`, Gradle files, Spring/config sources;
- Go: `go.mod`, command/package layout;
- Rust: `Cargo.toml`, workspace crates;
- .NET: solution/project files and application startup;
- mobile: Expo/EAS, React Native, Android Gradle, Xcode project/workspace evidence;
- data: ORM models, migrations, database config, query layers;
- delivery: CI workflows, Docker/Compose, Kubernetes, Terraform, hosting config;
- quality: actual lint/typecheck/test scripts and configurations;
- existing agents: `.codex/agents/*.toml`, `.codex/config.toml`, plan templates.

Do not perform broad scans when a manifest and a few entrypoints answer the question.

## Project profile schema

Build this internal profile before editing:

```text
ROOT:
PROJECT TYPE: client | backend | full-stack | mobile | data | infrastructure | monorepo | other
LANGUAGES / VERSIONS:
FRAMEWORKS / VERSIONS:
PACKAGE MANAGER / LOCKFILE:
DEPLOYABLES:
ARCHITECTURE / LAYERS:
ENTRYPOINTS / REQUEST FLOW:
DATA / MIGRATIONS:
AUTH / TRUST BOUNDARIES:
UPLOADS / FILESYSTEM:
EXTERNAL INTEGRATIONS:
BUILD / LINT / TYPECHECK:
TESTS:
CI / DEPLOYMENT / CONTAINERS:
STRUCTURAL DOC RULES:
EXISTING AGENT SETUP:
KNOWN ABSENCES:
SOURCE-TEMPLATE TERMS TO FORBID:
EVIDENCE:
```

Do not continue to generation while a material field is ambiguous enough to change team composition.

## Worker selection

Choose the narrowest primary worker that owns the normal implementation path:

| Evidence-backed project shape | Default primary worker | Typical scope |
| --- | --- | --- |
| React/Vite/SPA/client-only | `frontend_worker` | components, hooks, state, routing, accessibility, client API adapters |
| Next.js or similar tightly coupled app | `fullstack_worker` | routes/server actions, UI, shared contracts, persistence when present |
| FastAPI/Django/Flask/NestJS/Spring/Go API | `backend_worker` | endpoints, validation, services, persistence, auth, integrations |
| Expo/React Native/native app | `mobile_worker` | navigation, native UI, device APIs, builds when in scope |
| ETL/analytics/ML pipeline | `data_worker` | pipelines, schemas, transformations, model/data validation |
| Terraform/Kubernetes/platform repo | `infra_worker` | infrastructure code, deployment, secrets boundaries, rollout |
| Library/CLI/unclear single surface | `implementation_worker` | project-native source and packaging |

For a monorepo, create separate workers only when deployables have independent tooling/ownership and the
multi-agent gate will materially benefit. Otherwise use one primary worker with explicit per-task scope.

Add `fast_worker` only when the repository has common mechanical work that can be safely excluded from:

- authentication/authorization and secrets;
- database access/schema/migrations;
- uploads/filesystem/networking/integrations;
- public API or validation behavior;
- domain-critical rules, concurrency, and deployment.

## Contract vocabulary adaptation

Replace generic/source terminology with project-native terms:

| Concern | Adapt from evidence |
| --- | --- |
| UI | component model, router, state/data-fetching approach, styling, accessibility, build tool |
| API | route/controller/handler model, validation/schema types, middleware/dependencies/guards |
| Business logic | services/use cases/domain modules actually present; do not invent a layer |
| Data | ORM/query library, session/transaction model, migrations, model registration |
| Auth | actual token/session/provider, server/client enforcement points, roles/ownership |
| Tests | actual framework, scripts, environments, and whether tests exist |
| Tooling | exact package manager and manifest scripts; never translate commands by habit |
| Docs | canonical files and required structural documentation workflow |
| Deployment | only files/providers that exist or are explicitly requested |

Examples:

- React/Vite: refer to components/hooks/routes, TypeScript, npm/pnpm/yarn/bun only as evidenced,
  ESLint/typecheck/Vitest only if configured, browser auth and client-side secret boundaries.
- FastAPI/SQLModel: refer to routers/dependencies/Pydantic models/sessions/Alembic only if present,
  and use the repository's actual Python manager and sync/async model.
- NestJS/TypeORM: refer to modules/controllers/providers/DTOs/guards/entities/migrations only if present.
- Django: refer to apps/views/serializers/forms/models/migrations/middleware only if present.
- Spring: refer to controllers/services/repositories/entities/config/security and Gradle/Maven as evidenced.

## Risk adaptation

Security Reviewer and Validator must focus on affected trust boundaries, not a generic checklist dump.

- Client UI: XSS, unsafe HTML, token storage, exposed secrets, open redirects, dependency/supply chain.
- Backend: authn/authz, IDOR, injection, mass assignment, validation, rate limits, sensitive responses.
- Data/migrations: transactionality, destructive changes, compatibility, rollback, tenant/ownership filters.
- Uploads: size/type/path validation, public exposure, malware handling, storage permissions.
- Infrastructure: IAM, secrets, network exposure, state safety, rollout/rollback, CI credentials.
- Integrations: SSRF, signature verification, retries/idempotency, credential leakage, untrusted responses.

## Contamination review

Before completion:

1. Search generated files for source-project frameworks, paths, commands, integrations, and role names.
2. Confirm every surviving specific term exists in the target or explicit request.
3. Confirm absent capabilities are stated as absent rather than silently scaffolded.
4. Confirm worker responsibilities match real architecture rather than an idealized rewrite.
