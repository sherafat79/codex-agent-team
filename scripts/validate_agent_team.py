#!/usr/bin/env python3
"""Read-only validation for a project-specific Codex multi-agent installation."""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path


HEADINGS = (
    "## ROLE",
    "## OBJECTIVE",
    "## INPUTS",
    "## RESPONSIBILITIES",
    "## PERMISSIONS",
    "## STOP / ESCALATION CONDITIONS",
    "## OUTPUT SCHEMA",
)

OBJECTIVES = (
    "How does it work now?",
    "How should we change it?",
    "Make the change.",
    "Did we break anything?",
    "Did we create a security problem?",
    "Did we actually satisfy the request?",
)

READ_ONLY_OBJECTIVES = {
    "How does it work now?",
    "How should we change it?",
    "Did we create a security problem?",
    "Did we actually satisfy the request?",
}

SCOPED_WRITE_OBJECTIVES = {
    "Make the change.",
    "Did we break anything?",
}

DELEGATION_FIELDS = (
    "INPUT",
    "SCOPE",
    "CONSTRAINTS",
    "EXPECTED OUTPUT",
    "STOP CONDITIONS",
)

PLACEHOLDER_PATTERN = re.compile(r"\bTODO\b|\[TODO|\{\{|\}\}", re.IGNORECASE)


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Codex Agent Contracts and orchestrator integration."
    )
    parser.add_argument("--project", type=Path, required=True, help="Target repository root")
    parser.add_argument(
        "--plan-file",
        default="PLANS.md",
        help="Plan template path relative to the project root (default: PLANS.md)",
    )
    parser.add_argument(
        "--forbid-term",
        action="append",
        default=[],
        help="Evidence-backed irrelevant source-stack term; repeat as needed",
    )
    return parser.parse_args()


def read_text(path: Path, validation: Validation) -> str | None:
    if not path.is_file():
        validation.error(f"missing required file: {path}")
        return None

    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        validation.error(f"cannot read {path}: {exc}")
        return None


def validate_text(path: Path, text: str, validation: Validation) -> None:
    if PLACEHOLDER_PATTERN.search(text):
        validation.error(f"unresolved placeholder in {path}")

    trailing_lines = [
        number
        for number, line in enumerate(text.splitlines(), start=1)
        if line.rstrip() != line
    ]
    if trailing_lines:
        validation.error(f"trailing whitespace in {path} at lines {trailing_lines}")

    if text and not text.endswith("\n"):
        validation.warning(f"file does not end with a newline: {path}")


def validate_contract(
    path: Path,
    data: dict[str, object],
    validation: Validation,
) -> str | None:
    name = data.get("name")
    description = data.get("description")
    sandbox = data.get("sandbox_mode")
    instructions = data.get("developer_instructions")

    if not isinstance(name, str) or not name:
        validation.error(f"{path}: missing string name")
    elif path.stem.replace("-", "_") != name:
        validation.error(f"{path}: filename does not match agent name {name!r}")

    if not isinstance(description, str) or not description.strip():
        validation.error(f"{path}: missing non-empty description")

    if not isinstance(instructions, str) or not instructions.strip():
        validation.error(f"{path}: missing developer_instructions")
        return None

    positions: list[int] = []
    for heading in HEADINGS:
        count = instructions.count(heading)
        if count != 1:
            validation.error(f"{path}: expected exactly one {heading!r}, found {count}")
        positions.append(instructions.find(heading))

    if all(position >= 0 for position in positions) and positions != sorted(positions):
        validation.error(f"{path}: Agent Contract headings are out of order")

    matching_objectives = [objective for objective in OBJECTIVES if objective in instructions]
    if len(matching_objectives) != 1:
        validation.error(
            f"{path}: expected one distinct objective, found {matching_objectives or 'none'}"
        )
        objective = None
    else:
        objective = matching_objectives[0]

    missing_fields = [field for field in DELEGATION_FIELDS if field not in instructions]
    if missing_fields:
        validation.error(f"{path}: missing delegation fields {missing_fields}")

    if objective in READ_ONLY_OBJECTIVES:
        if sandbox != "read-only":
            validation.error(f"{path}: {objective!r} must use sandbox_mode = 'read-only'")
        if "READ ONLY" not in instructions.upper():
            validation.error(f"{path}: read-only permission is not explicit in the contract")

    if objective in SCOPED_WRITE_OBJECTIVES:
        if sandbox != "workspace-write":
            validation.error(f"{path}: {objective!r} must use sandbox_mode = 'workspace-write'")
        if "SCOPED WRITE" not in instructions.upper():
            validation.error(f"{path}: scoped-write permission is not explicit in the contract")

    validate_text(path, path.read_text(encoding="utf-8"), validation)
    return objective


def validate_config(path: Path, validation: Validation) -> None:
    text = read_text(path, validation)
    if text is None:
        return

    validate_text(path, text, validation)
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        validation.error(f"invalid TOML in {path}: {exc}")
        return

    agents = data.get("agents")
    if not isinstance(agents, dict):
        validation.error(f"{path}: missing [agents] table")
        return

    max_threads = agents.get("max_threads")
    max_depth = agents.get("max_depth")
    if not isinstance(max_threads, int) or max_threads < 2:
        validation.error(f"{path}: agents.max_threads must be an integer >= 2")
    if max_depth != 1:
        validation.error(f"{path}: agents.max_depth must be 1 so root owns delegation")


def validate_workflow_file(
    path: Path,
    validation: Validation,
    *,
    require_questions: bool,
) -> str | None:
    text = read_text(path, validation)
    if text is None:
        return None

    validate_text(path, text, validation)
    missing_fields = [field for field in DELEGATION_FIELDS if field not in text]
    if missing_fields:
        validation.error(f"{path}: missing delegation fields {missing_fields}")

    if require_questions:
        missing_objectives = [objective for objective in OBJECTIVES if objective not in text]
        if missing_objectives:
            validation.error(f"{path}: missing agent questions/jobs {missing_objectives}")

    return text


def validate_forbidden_terms(
    paths_and_text: list[tuple[Path, str]],
    terms: list[str],
    validation: Validation,
) -> None:
    for term in terms:
        normalized = term.strip()
        if not normalized:
            continue
        for path, text in paths_and_text:
            if normalized.casefold() in text.casefold():
                validation.error(f"forbidden source-stack term {normalized!r} found in {path}")


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    validation = Validation()

    if not project.is_dir():
        print(f"ERROR: project directory does not exist: {project}", file=sys.stderr)
        return 2

    agents_dir = project / ".codex" / "agents"
    agent_paths = sorted(agents_dir.glob("*.toml")) if agents_dir.is_dir() else []
    if not agent_paths:
        validation.error(f"no agent TOML files found under {agents_dir}")

    objectives_found: set[str] = set()
    names_found: set[str] = set()
    collected: list[tuple[Path, str]] = []

    for path in agent_paths:
        text = read_text(path, validation)
        if text is None:
            continue
        collected.append((path, text))
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            validation.error(f"invalid TOML in {path}: {exc}")
            continue

        name = data.get("name")
        if isinstance(name, str):
            if name in names_found:
                validation.error(f"duplicate agent name: {name}")
            names_found.add(name)

        objective = validate_contract(path, data, validation)
        if objective:
            objectives_found.add(objective)

    missing_objectives = [objective for objective in OBJECTIVES if objective not in objectives_found]
    if missing_objectives:
        validation.error(f"agent team does not cover questions/jobs {missing_objectives}")

    validate_config(project / ".codex" / "config.toml", validation)

    agents_md = project / "AGENTS.md"
    agents_text = validate_workflow_file(
        agents_md,
        validation,
        require_questions=True,
    )
    if agents_text is not None:
        collected.append((agents_md, agents_text))

    plan_path = project / args.plan_file
    plan_text = validate_workflow_file(
        plan_path,
        validation,
        require_questions=True,
    )
    if plan_text is not None:
        collected.append((plan_path, plan_text))

    validate_forbidden_terms(collected, args.forbid_term, validation)

    for warning in validation.warnings:
        print(f"WARNING: {warning}")
    for error in validation.errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if validation.errors:
        print(
            f"FAILED: {len(validation.errors)} error(s), {len(validation.warnings)} warning(s)",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: validated {len(agent_paths)} Agent Contract(s), orchestrator workflow, "
        f"and plan template in {project}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
