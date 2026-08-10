#!/usr/bin/env python3
"""Read-only validation for a project-specific Codex agent-team installation."""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path


HEADINGS = (
    "ROLE",
    "OBJECTIVE",
    "INPUTS",
    "RESPONSIBILITIES",
    "PERMISSIONS",
    "STOP / ESCALATION CONDITIONS",
    "OUTPUT",
)

CAPABILITIES = {
    "exploration": ("required", "How does it work now?"),
    "implementation": ("required", "Make the change."),
    "validation": ("required", "Did we actually satisfy the request?"),
    "architecture": ("conditional", "How should we change it?"),
    "regression_assessment": ("conditional", "Did we break anything?"),
    "security_review": ("conditional", "Did we create a security problem?"),
}

OBJECTIVES = tuple(value[1] for value in CAPABILITIES.values())
READ_ONLY_OBJECTIVES = {
    "How does it work now?",
    "How should we change it?",
    "Did we create a security problem?",
    "Did we actually satisfy the request?",
}
SCOPED_WRITE_OBJECTIVES = {"Make the change.", "Did we break anything?"}

HANDOFF_FIELDS = (
    "OBJECTIVE",
    "SCOPE",
    "INPUT EVIDENCE",
    "REQUIRED BEHAVIOR",
    "CONSTRAINTS",
    "MUST PRESERVE",
    "MUST NOT CHANGE",
    "ACCEPTANCE CRITERIA",
    "ESCALATION CONDITIONS",
    "EXPECTED OUTPUT",
)

PROJECT_TYPES = {
    "backend",
    "frontend",
    "fullstack",
    "library",
    "infrastructure",
    "monorepo",
    "other",
}
FEATURES = {
    "http_api",
    "persistence",
    "authentication",
    "authorization",
    "uploads",
    "external_integrations",
    "background_jobs",
    "networking",
    "infrastructure",
}
RISK_AREAS = {"authentication", "data", "infrastructure", "external_integration"}
RISK_LEVELS = {"low", "medium", "high"}
CAPABILITY_MODES = {"root", "agent", "existing_specialist", "conditional", "not_applicable"}

PLACEHOLDER_PATTERN = re.compile(r"\bTODO\b|\[TODO|\{\{|\}\}", re.IGNORECASE)
HEADING_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
WRITE_ACTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bapply(?:ing)?\s+(?:a\s+)?patch\b",
        r"\b(?:modify|edit|write|create|delete|remove)(?:ing)?\s+(?:tracked\s+)?files?\b",
        r"\bgit\s+(?:add|commit|push)\b",
        r"\bcreate(?:s|d|ing)?\s+(?:a\s+)?migrations?\b",
        r"\binstall(?:s|ed|ing)?\s+dependencies\b",
    )
)
NEGATION_PATTERN = re.compile(
    r"\b(?:do\s+not|must\s+not|never|cannot|can't|forbid(?:s|den)?|without|no\s+permission\s+to)\b",
    re.IGNORECASE,
)


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
        description="Validate Codex Agent Contracts and root-owned orchestration."
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
        number for number, line in enumerate(text.splitlines(), start=1) if line.rstrip() != line
    ]
    if trailing_lines:
        validation.error(f"trailing whitespace in {path} at lines {trailing_lines}")
    if text and not text.endswith("\n"):
        validation.warning(f"file does not end with a newline: {path}")


def normalized(value: str) -> str:
    return " ".join(value.casefold().replace("_", " ").split())


def extract_sections(path: Path, instructions: str, validation: Validation) -> dict[str, str]:
    matches = list(HEADING_PATTERN.finditer(instructions))
    found = [normalized(match.group(1)).upper() for match in matches]
    expected = [normalized(heading).upper() for heading in HEADINGS]
    if found != expected:
        validation.error(
            f"{path}: Agent Contract headings must be exactly {list(HEADINGS)} in order; found {found}"
        )
        return {}
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(instructions)
        sections[HEADINGS[index]] = instructions[match.end() : end].strip()
    return sections


def contains_positive_write_action(text: str) -> str | None:
    for line in text.splitlines():
        for clause in re.split(r"[.;]", line):
            for pattern in WRITE_ACTION_PATTERNS:
                for match in pattern.finditer(clause):
                    prefix = clause[max(0, match.start() - 60) : match.start()]
                    if not NEGATION_PATTERN.search(prefix):
                        return match.group(0)
    return None


def has_scope_restriction(text: str) -> bool:
    value = normalized(text)
    scope = any(phrase in value for phrase in ("scope", "assigned path", "owned file"))
    limit = any(
        phrase in value
        for phrase in ("only", "limited", "restricted", "within", "outside assigned")
    )
    return scope and limit


def expected_objective_for_name(name: str) -> str | None:
    exact = {
        "explorer": "How does it work now?",
        "architect": "How should we change it?",
        "test_engineer": "Did we break anything?",
        "security_reviewer": "Did we create a security problem?",
        "validator": "Did we actually satisfy the request?",
    }
    if name in exact:
        return exact[name]
    if name.endswith("_worker"):
        return "Make the change."
    return None


def validate_contract(
    path: Path,
    data: dict[str, object],
    validation: Validation,
) -> tuple[str, str] | None:
    name = data.get("name")
    description = data.get("description")
    sandbox = data.get("sandbox_mode")
    instructions = data.get("developer_instructions")

    if not isinstance(name, str) or not name:
        validation.error(f"{path}: missing string name")
        return None
    if path.stem.replace("-", "_") != name:
        validation.error(f"{path}: filename does not match agent name {name!r}")
    if name == "fast_worker":
        validation.error(f"{path}: fast_worker is deprecated; migrate it to mechanical_worker")
    if not isinstance(description, str) or not description.strip():
        validation.error(f"{path}: missing non-empty description")
    if not isinstance(instructions, str) or not instructions.strip():
        validation.error(f"{path}: missing developer_instructions")
        return None

    sections = extract_sections(path, instructions, validation)
    if not sections:
        validate_text(path, path.read_text(encoding="utf-8"), validation)
        return None

    objective_section = sections["OBJECTIVE"]
    matching_objectives = [
        objective for objective in OBJECTIVES if objective.casefold() in objective_section.casefold()
    ]
    if len(matching_objectives) != 1:
        validation.error(
            f"{path}: OBJECTIVE must contain one distinct supported question/job; "
            f"found {matching_objectives or 'none'}"
        )
        objective = None
    else:
        objective = matching_objectives[0]

    expected_objective = expected_objective_for_name(name)
    if expected_objective and objective and objective != expected_objective:
        validation.error(
            f"{path}: agent name {name!r} contradicts objective {objective!r}"
        )

    inputs = normalized(sections["INPUTS"])
    missing_fields = [field for field in HANDOFF_FIELDS if normalized(field) not in inputs]
    if missing_fields:
        validation.error(f"{path}: INPUTS is missing handoff fields {missing_fields}")

    stop = normalized(sections["STOP / ESCALATION CONDITIONS"])
    if not any(word in stop for word in ("stop", "escalat")):
        validation.error(f"{path}: stop conditions must require stopping or escalation")
    if not any(word in stop for word in ("missing", "ambiguous", "contradictory")):
        validation.error(f"{path}: stop conditions must cover invalid or incomplete handoffs")

    if objective in READ_ONLY_OBJECTIVES:
        if sandbox != "read-only":
            validation.error(f"{path}: {objective!r} must use sandbox_mode = 'read-only'")
        if "read only" not in normalized(sections["PERMISSIONS"]):
            validation.error(f"{path}: PERMISSIONS must explicitly say read-only")
        write_action = contains_positive_write_action(
            sections["RESPONSIBILITIES"]
            + "\n"
            + sections["PERMISSIONS"]
            + "\n"
            + sections["STOP / ESCALATION CONDITIONS"]
        )
        if write_action:
            validation.error(
                f"{path}: read-only contract contains positive write behavior {write_action!r}"
            )

    if objective in SCOPED_WRITE_OBJECTIVES:
        if sandbox != "workspace-write":
            validation.error(f"{path}: {objective!r} must use sandbox_mode = 'workspace-write'")
        if not has_scope_restriction(sections["PERMISSIONS"]):
            validation.error(
                f"{path}: PERMISSIONS must limit writes to assigned paths/files in SCOPE"
            )

    if name == "mechanical_worker":
        contract = normalized(instructions)
        if not any(word in contract for word in ("deterministic", "mechanical", "repetitive")):
            validation.error(f"{path}: mechanical_worker must be limited to mechanical edits")
        if not all(word in stop for word in ("architectural", "security")) or not any(
            phrase in stop for phrase in ("data model", "data-model")
        ):
            validation.error(
                f"{path}: mechanical_worker must escalate architectural, security, and data-model judgment"
            )

    validate_text(path, path.read_text(encoding="utf-8"), validation)
    return (name, objective) if objective else None


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
    if not isinstance(max_threads, int) or isinstance(max_threads, bool) or max_threads < 1:
        validation.error(f"{path}: agents.max_threads must be an integer >= 1")
    if agents.get("max_depth") != 1:
        validation.error(f"{path}: agents.max_depth must be 1 so root owns delegation")


def validate_string_list(path: Path, label: str, value: object, validation: Validation) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        validation.error(f"{path}: {label} must be a list of non-empty strings")


def validate_profile(
    path: Path,
    contracts: dict[str, str],
    validation: Validation,
) -> None:
    text = read_text(path, validation)
    if text is None:
        return
    validate_text(path, text, validation)
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        validation.error(f"invalid TOML in {path}: {exc}")
        return

    version = data.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version != 1:
        validation.error(f"{path}: version must be 1")

    project = data.get("project")
    if not isinstance(project, dict):
        validation.error(f"{path}: missing [project] profile")
    else:
        if project.get("type") not in PROJECT_TYPES:
            validation.error(f"{path}: project.type must be one of {sorted(PROJECT_TYPES)}")
        validate_string_list(path, "project.evidence", project.get("evidence"), validation)

    stack = data.get("stack")
    if not isinstance(stack, dict):
        validation.error(f"{path}: missing [stack] profile")
    else:
        validate_string_list(path, "stack.languages", stack.get("languages"), validation)
        validate_string_list(path, "stack.frameworks", stack.get("frameworks"), validation)
        validate_string_list(path, "stack.deployment", stack.get("deployment"), validation)
        database = stack.get("database")
        if database is not None and (not isinstance(database, str) or not database.strip()):
            validation.error(f"{path}: stack.database must be a non-empty string when present")

    features = data.get("features")
    if not isinstance(features, dict):
        validation.error(f"{path}: missing [features] profile")
    else:
        missing = sorted(FEATURES - features.keys())
        unknown = sorted(features.keys() - FEATURES)
        if missing:
            validation.error(f"{path}: missing feature declarations {missing}")
        if unknown:
            validation.error(f"{path}: unknown feature declarations {unknown}")
        for name, value in features.items():
            if name in FEATURES and not isinstance(value, bool):
                validation.error(f"{path}: features.{name} must be boolean")

    risk = data.get("risk")
    if not isinstance(risk, dict):
        validation.error(f"{path}: missing [risk] profile")
    else:
        missing = sorted(RISK_AREAS - risk.keys())
        unknown = sorted(risk.keys() - RISK_AREAS)
        if missing:
            validation.error(f"{path}: missing risk declarations {missing}")
        if unknown:
            validation.error(f"{path}: unknown risk declarations {unknown}")
        for name, value in risk.items():
            if name in RISK_AREAS and value not in RISK_LEVELS:
                validation.error(f"{path}: risk.{name} must be low, medium, or high")

    capabilities = data.get("capabilities")
    if not isinstance(capabilities, dict):
        validation.error(f"{path}: missing [capabilities] map")
        return
    missing = sorted(CAPABILITIES.keys() - capabilities.keys())
    unknown = sorted(capabilities.keys() - CAPABILITIES.keys())
    if missing:
        validation.error(f"{path}: missing capability declarations {missing}")
    if unknown:
        validation.error(f"{path}: unknown capability declarations {unknown}")

    for capability, (requirement, objective) in CAPABILITIES.items():
        declaration = capabilities.get(capability)
        label = f"capabilities.{capability}"
        if not isinstance(declaration, dict):
            if declaration is not None:
                validation.error(f"{path}: {label} must be a table")
            continue
        mode = declaration.get("mode")
        agent = declaration.get("agent")
        justification = declaration.get("justification")
        if mode not in CAPABILITY_MODES:
            validation.error(f"{path}: {label}.mode must be one of {sorted(CAPABILITY_MODES)}")
            continue
        if requirement == "required" and mode in {"conditional", "not_applicable"}:
            validation.error(f"{path}: required capability {capability} cannot use mode {mode!r}")
        if mode in {"root", "conditional", "not_applicable"}:
            if agent is not None:
                validation.error(f"{path}: {label} mode {mode!r} contradicts an agent assignment")
            if not isinstance(justification, str) or not justification.strip():
                validation.error(f"{path}: {label} mode {mode!r} requires a justification")
        if mode in {"agent", "existing_specialist"}:
            if not isinstance(agent, str) or not agent:
                validation.error(f"{path}: {label} mode {mode!r} requires an agent name")
            elif agent not in contracts:
                validation.error(f"{path}: {label} references missing agent {agent!r}")
            elif contracts[agent] != objective:
                validation.error(
                    f"{path}: {label} agent {agent!r} has objective {contracts[agent]!r}, "
                    f"expected {objective!r}"
                )
            if justification is not None and not isinstance(justification, str):
                validation.error(f"{path}: {label}.justification must be a string")


def validate_workflow_file(path: Path, validation: Validation) -> str | None:
    text = read_text(path, validation)
    if text is None:
        return None
    validate_text(path, text, validation)
    value = normalized(text)
    missing_fields = [field for field in HANDOFF_FIELDS if normalized(field) not in value]
    if missing_fields:
        validation.error(f"{path}: missing handoff fields {missing_fields}")
    return text


def validate_forbidden_terms(
    paths_and_text: list[tuple[Path, str]],
    terms: list[str],
    validation: Validation,
) -> None:
    for term in terms:
        term = term.strip()
        if not term:
            continue
        for path, text in paths_and_text:
            if term.casefold() in text.casefold():
                validation.error(f"forbidden source-stack term {term!r} found in {path}")


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    validation = Validation()
    if not project.is_dir():
        print(f"ERROR: project directory does not exist: {project}", file=sys.stderr)
        return 2

    agents_dir = project / ".codex" / "agents"
    agent_paths = sorted(agents_dir.glob("*.toml")) if agents_dir.is_dir() else []
    contracts: dict[str, str] = {}
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
        result = validate_contract(path, data, validation)
        if result:
            name, objective = result
            if name in contracts:
                validation.error(f"duplicate agent name: {name}")
            contracts[name] = objective

    validate_config(project / ".codex" / "config.toml", validation)
    validate_profile(project / ".codex" / "agent-team.toml", contracts, validation)

    for workflow_path in (project / "AGENTS.md", project / args.plan_file):
        workflow_text = validate_workflow_file(workflow_path, validation)
        if workflow_text is not None:
            collected.append((workflow_path, workflow_text))

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

    print("CAPABILITY COVERAGE: PASS")
    print("LEAST PRIVILEGE: PASS")
    print("HANDOFF CONTRACTS: PASS")
    print("ORCHESTRATION DEPTH: PASS")
    print(
        f"OK: validated project profile, capability coverage, {len(agent_paths)} Agent Contract(s), "
        f"root-owned orchestration, and plan template in {project}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
