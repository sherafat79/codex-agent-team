from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "codex-agent-team"
VALIDATOR = SKILL_ROOT / "scripts" / "validate_agent_team.py"

ROLE_OBJECTIVES = {
    "explorer": "How does it work now?",
    "architect": "How should we change it?",
    "implementation_worker": "Make the change.",
    "mechanical_worker": "Make the change.",
    "test_engineer": "Did we break anything?",
    "security_reviewer": "Did we create a security problem?",
    "validator": "Did we actually satisfy the request?",
}
READ_ONLY = {"explorer", "architect", "security_reviewer", "validator"}
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
DEFAULT_ROLES = ("explorer", "implementation_worker", "validator")


def contract_text(name: str) -> str:
    objective = ROLE_OBJECTIVES[name]
    if name in READ_ONLY:
        sandbox = "read-only"
        responsibilities = "Inspect scoped evidence without modifying files."
        permissions = "READ ONLY. Targeted inspection only; never write files."
    else:
        sandbox = "workspace-write"
        responsibilities = "Implement only the assigned change using the smallest safe diff."
        permissions = "SCOPED WRITE. Write only to exact files assigned in SCOPE; never edit outside it."

    stop = "Stop and escalate when inputs are missing, ambiguous, or contradictory."
    if name == "mechanical_worker":
        responsibilities = "Perform only deterministic, repetitive mechanical edits."
        stop += " Stop for architectural, security, or data-model judgment and escalate to root."

    return f'''name = "{name}"
description = "Test contract"
sandbox_mode = "{sandbox}"
developer_instructions = """
## ROLE
Test role.
## OBJECTIVE
{objective}
## INPUTS
Require {", ".join(HANDOFF_FIELDS)}.
## RESPONSIBILITIES
{responsibilities}
## PERMISSIONS
{permissions}
## STOP / ESCALATION CONDITIONS
{stop}
## OUTPUT
Return status and evidence.
"""
'''


def write_profile(
    project: Path,
    capability_overrides: dict[str, tuple[str, str | None, str | None]] | None = None,
) -> None:
    capabilities = {
        "exploration": ("agent", "explorer", None),
        "implementation": ("agent", "implementation_worker", None),
        "validation": ("agent", "validator", None),
        "architecture": ("conditional", None, "Use only when design judgment is material."),
        "regression_assessment": ("conditional", None, "Activate according to changed behavior and risk."),
        "security_review": ("conditional", None, "Activate when a trust boundary changes."),
    }
    capabilities.update(capability_overrides or {})

    lines = [
        "version = 1",
        "",
        "[project]",
        'type = "library"',
        'evidence = ["AGENTS.md", ".codex/config.toml"]',
        "",
        "[stack]",
        'languages = ["Python", "Markdown"]',
        "frameworks = []",
        'package_manager = "none"',
        "deployment = []",
        "",
        "[features]",
        "http_api = false",
        "persistence = false",
        "authentication = false",
        "authorization = false",
        "uploads = false",
        "external_integrations = false",
        "background_jobs = false",
        "networking = false",
        "infrastructure = false",
        "",
        "[risk]",
        'authentication = "low"',
        'data = "low"',
        'infrastructure = "low"',
        'external_integration = "low"',
    ]
    for capability, (mode, agent, justification) in capabilities.items():
        lines.extend(("", f"[capabilities.{capability}]", f'mode = "{mode}"'))
        if agent is not None:
            lines.append(f'agent = "{agent}"')
        if justification is not None:
            lines.append(f'justification = "{justification}"')
    (project / ".codex" / "agent-team.toml").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_valid_project(
    project: Path,
    *,
    max_threads: int = 4,
    max_depth: int = 1,
    roles: tuple[str, ...] = DEFAULT_ROLES,
    capability_overrides: dict[str, tuple[str, str | None, str | None]] | None = None,
) -> None:
    agents = project / ".codex" / "agents"
    agents.mkdir(parents=True)
    (project / ".codex" / "config.toml").write_text(
        f"[agents]\nmax_threads = {max_threads}\nmax_depth = {max_depth}\n",
        encoding="utf-8",
    )
    for name in roles:
        filename = name.replace("_", "-") + ".toml"
        (agents / filename).write_text(contract_text(name), encoding="utf-8")
    write_profile(project, capability_overrides)

    workflow = "\n".join(
        (
            "Root Orchestrator owns every delegation; max_depth remains one.",
            "Independent Review / Context Isolation passes objective evidence, not persuasive conclusions.",
            "Exclusive write ownership is required; parallel work must be independent.",
            *HANDOFF_FIELDS,
            "",
        )
    )
    (project / "AGENTS.md").write_text(workflow, encoding="utf-8")
    (project / "PLANS.md").write_text(workflow, encoding="utf-8")


class PublicPackageTests(unittest.TestCase):
    def run_validator(self, project: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--project", str(project)],
            capture_output=True,
            check=False,
            text=True,
        )

    def assert_rejected(self, result: subprocess.CompletedProcess[str], phrase: str) -> None:
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(phrase, result.stderr)

    def test_skill_metadata_uses_public_name(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        metadata = skill.split("---", 2)[1]
        self.assertIn("name: codex-agent-team", metadata)

        interface = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Codex Agent Team"', interface)
        self.assertIn("$codex-agent-team", interface)
        self.assertNotIn("bootstrap-agent-team", skill + interface)

    def test_isolated_skill_subtree_is_self_contained(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            isolated_skill = temporary_root / "codex-agent-team"
            shutil.copytree(SKILL_ROOT, isolated_skill)

            for relative_path in (
                "SKILL.md",
                "agents/openai.yaml",
                "references/agent-contracts.md",
                "references/capability-model.md",
                "references/complexity-gate.md",
                "references/handoff-protocol.md",
                "references/stack-adaptation.md",
                "scripts/validate_agent_team.py",
            ):
                self.assertTrue((isolated_skill / relative_path).is_file(), relative_path)

            for repository_only_name in (
                ".github",
                "docs",
                "tests",
                "examples",
                "README.md",
                "LICENSE",
            ):
                self.assertFalse((isolated_skill / repository_only_name).exists())
            self.assertFalse(
                any(path.suffix.lower() in {".gif", ".jpg", ".jpeg", ".png", ".webp"}
                    for path in isolated_skill.rglob("*"))
            )

            project = temporary_root / "project"
            write_valid_project(project)
            result = subprocess.run(
                [
                    sys.executable,
                    str(isolated_skill / "scripts" / "validate_agent_team.py"),
                    "--project",
                    str(project),
                ],
                capture_output=True,
                check=False,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_accepts_capability_driven_team(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project)
            result = self.run_validator(project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CAPABILITY COVERAGE: PASS", result.stdout)
        self.assertIn("LEAST PRIVILEGE: PASS", result.stdout)
        self.assertIn("HANDOFF CONTRACTS: PASS", result.stdout)
        self.assertIn("ORCHESTRATION DEPTH: PASS", result.stdout)
        self.assertIn("capability coverage, 3 Agent Contract(s)", result.stdout)

    def test_checked_in_examples_are_validator_ready(self) -> None:
        examples = REPO_ROOT / "examples"
        fixtures = sorted(path.parent.parent for path in examples.glob("*/.codex/agent-team.toml"))
        self.assertEqual(
            [path.name for path in fixtures],
            ["jwt-refresh", "root-only-typo"],
        )
        for fixture in fixtures:
            with self.subTest(fixture=fixture.name):
                result = self.run_validator(fixture)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("CAPABILITY COVERAGE: PASS", result.stdout)

    def test_max_threads_one_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project, max_threads=1)
            result = self.run_validator(project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_non_positive_max_threads_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project, max_threads=0)
            result = self.run_validator(project)
        self.assert_rejected(result, "agents.max_threads must be an integer >= 1")

    def test_max_depth_other_than_one_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project, max_depth=2)
            result = self.run_validator(project)
        self.assert_rejected(result, "agents.max_depth must be 1")

    def test_read_only_contract_with_write_behavior_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project)
            path = project / ".codex" / "agents" / "explorer.toml"
            text = path.read_text(encoding="utf-8").replace(
                "Inspect scoped evidence without modifying files.",
                "Modify files and apply a patch when useful.",
            )
            path.write_text(text, encoding="utf-8")
            result = self.run_validator(project)
        self.assert_rejected(result, "read-only contract contains positive write behavior")

    def test_worker_without_meaningful_scope_restriction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project)
            path = project / ".codex" / "agents" / "implementation-worker.toml"
            text = path.read_text(encoding="utf-8").replace(
                "SCOPED WRITE. Write only to exact files assigned in SCOPE; never edit outside it.",
                "SCOPED WRITE.",
            )
            path.write_text(text, encoding="utf-8")
            result = self.run_validator(project)
        self.assert_rejected(result, "must limit writes to assigned paths/files in SCOPE")

    def test_mechanical_worker_is_recognized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(
                project,
                roles=("explorer", "mechanical_worker", "validator"),
                capability_overrides={
                    "implementation": ("agent", "mechanical_worker", None),
                },
            )
            result = self.run_validator(project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fast_worker_is_rejected_with_migration_message(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project)
            old = project / ".codex" / "agents" / "implementation-worker.toml"
            new = project / ".codex" / "agents" / "fast-worker.toml"
            new.write_text(
                contract_text("implementation_worker").replace(
                    'name = "implementation_worker"', 'name = "fast_worker"'
                ),
                encoding="utf-8",
            )
            old.unlink()
            write_profile(
                project,
                {"implementation": ("agent", "fast_worker", None)},
            )
            result = self.run_validator(project)
        self.assert_rejected(result, "fast_worker is deprecated; migrate it to mechanical_worker")

    def test_root_can_cover_required_capabilities_without_agents(self) -> None:
        overrides = {
            "exploration": ("root", None, "Small repository and bounded question."),
            "implementation": ("root", None, "Simple low-risk task."),
            "validation": ("root", None, "Root can independently check the small diff."),
        }
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project, roles=(), capability_overrides=overrides)
            result = self.run_validator(project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 Agent Contract(s)", result.stdout)

    def test_conditional_security_capability_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project)
            result = self.run_validator(project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_contradictory_capability_declaration_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(
                project,
                capability_overrides={
                    "implementation": ("conditional", None, "Maybe later."),
                },
            )
            result = self.run_validator(project)
        self.assert_rejected(result, "required capability implementation cannot use mode 'conditional'")

    def test_capability_agent_must_exist_and_match_objective(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(
                project,
                capability_overrides={
                    "security_review": ("agent", "validator", None),
                },
            )
            result = self.run_validator(project)
        self.assert_rejected(result, "expected 'Did we create a security problem?'")

    def test_contract_section_order_is_still_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project)
            path = project / ".codex" / "agents" / "explorer.toml"
            text = path.read_text(encoding="utf-8")
            text = text.replace("## ROLE\nTest role.\n## OBJECTIVE", "## OBJECTIVE")
            text = text.replace("## INPUTS", "## ROLE\nTest role.\n## INPUTS")
            path.write_text(text, encoding="utf-8")
            result = self.run_validator(project)
        self.assert_rejected(result, "Agent Contract headings must be exactly")

    def test_validator_rejects_unresolved_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project)
            path = project / ".codex" / "agents" / "explorer.toml"
            path.write_text(path.read_text(encoding="utf-8") + "# TODO\n", encoding="utf-8")
            result = self.run_validator(project)
        self.assert_rejected(result, "unresolved placeholder")


if __name__ == "__main__":
    unittest.main()
