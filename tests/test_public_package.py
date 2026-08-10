from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_agent_team.py"

ROLES = (
    ("explorer", "How does it work now?", "read-only", "READ ONLY"),
    ("architect", "How should we change it?", "read-only", "READ ONLY"),
    ("implementation_worker", "Make the change.", "workspace-write", "SCOPED WRITE"),
    ("test_engineer", "Did we break anything?", "workspace-write", "SCOPED WRITE"),
    (
        "security_reviewer",
        "Did we create a security problem?",
        "read-only",
        "READ ONLY",
    ),
    (
        "validator",
        "Did we actually satisfy the request?",
        "read-only",
        "READ ONLY",
    ),
)


def write_valid_project(project: Path) -> None:
    agents = project / ".codex" / "agents"
    agents.mkdir(parents=True)
    (project / ".codex" / "config.toml").write_text(
        "[agents]\nmax_threads = 6\nmax_depth = 1\n",
        encoding="utf-8",
    )

    for name, objective, sandbox, permission in ROLES:
        contract = f'''name = "{name}"
description = "Test contract"
sandbox_mode = "{sandbox}"
developer_instructions = """
## ROLE
Test role.
## OBJECTIVE
{objective}
## INPUTS
Require INPUT, SCOPE, CONSTRAINTS, EXPECTED OUTPUT, and STOP CONDITIONS.
## RESPONSIBILITIES
Perform the assigned job only.
## PERMISSIONS
{permission}.
## STOP / ESCALATION CONDITIONS
Stop on missing evidence.
## OUTPUT SCHEMA
Return status and evidence.
"""
'''
        (agents / f"{name.replace('_', '-')}.toml").write_text(contract, encoding="utf-8")

    workflow = "\n".join(
        [
            "INPUT SCOPE CONSTRAINTS EXPECTED OUTPUT STOP CONDITIONS",
            *(objective for _, objective, _, _ in ROLES),
            "",
        ]
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

    def test_skill_metadata_uses_public_name(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        metadata = skill.split("---", 2)[1]
        self.assertIn("name: codex-agent-team", metadata)

        interface = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Codex Agent Team"', interface)
        self.assertIn("$codex-agent-team", interface)
        self.assertNotIn("bootstrap-agent-team", skill + interface)

    def test_validator_accepts_complete_contract_team(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project)
            result = self.run_validator(project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK: validated 6 Agent Contract(s)", result.stdout)

    def test_validator_rejects_unresolved_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_valid_project(project)
            agent = project / ".codex" / "agents" / "explorer.toml"
            agent.write_text(agent.read_text(encoding="utf-8") + "# TODO\n", encoding="utf-8")
            result = self.run_validator(project)

        self.assertEqual(result.returncode, 1)
        self.assertIn("unresolved placeholder", result.stderr)


if __name__ == "__main__":
    unittest.main()
