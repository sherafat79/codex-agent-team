# codex-agent-team

A Codex skill that inspects a software repository and installs the smallest useful,
project-specific multi-agent team for its real stack, architecture, tooling, and risks.

It generates Agent Contracts under `.codex/agents/`, configures bounded orchestration,
and adds project-aware workflow and planning guidance without copying assumptions from
an unrelated framework.

## What it does

- Detects languages, frameworks, package managers, deployables, and architecture from repository evidence.
- Selects a minimal team covering exploration, architecture, implementation, testing, security, and validation.
- Adapts agent terminology, commands, permissions, and risks to the target repository.
- Preserves existing instructions and unrelated working-tree changes.
- Validates generated contracts, orchestration settings, and source-template contamination.

## Requirements

- Codex with support for skills and project agents.
- Python 3.11 or newer for the bundled validator.
- No third-party runtime dependencies.

## Install

Clone the repository into your personal Codex skills directory.

macOS or Linux:

```bash
git clone https://github.com/sherafat79/codex-agent-team.git ~/.agents/skills/codex-agent-team
```

Windows PowerShell:

```powershell
git clone https://github.com/sherafat79/codex-agent-team.git "$env:USERPROFILE\.agents\skills\codex-agent-team"
```

Codex detects skill changes automatically. If the skill does not appear, restart Codex.

## Use

Invoke the skill from the repository you want to configure:

```text
Use $codex-agent-team to inspect this repository and install an adaptive multi-agent team.
```

The skill may create or update:

```text
.codex/agents/*.toml
.codex/config.toml
AGENTS.md
PLANS.md
```

The root Codex session remains the orchestrator. Read-only roles cannot modify project
state, and write-capable roles receive explicit, non-overlapping ownership.

## Validate an installation

```bash
python ~/.agents/skills/codex-agent-team/scripts/validate_agent_team.py --project /path/to/project
```

Use `--plan-file` for a non-default plan template and repeat `--forbid-term` for
irrelevant source-stack terms that must not appear in generated workflow files.

## Development

Run the dependency-free test suite:

```bash
python -m unittest discover -s tests -v
```

## Security

Review generated Agent Contracts before using them on sensitive repositories. The skill
is designed to keep discovery and review roles read-only, but implementation agents can
edit files explicitly assigned to them.

Please report suspected vulnerabilities privately through the repository's GitHub
Security page rather than opening a public issue.

## License

[MIT](LICENSE)
