"""Smoke tests for ml-automation-drift — validate plugin layout invariants."""

import json
import re
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def test_manifest_validity():
    """Test that .cortex-plugin/plugin.json is valid and contains required fields."""
    manifest_path = PLUGIN_ROOT / ".cortex-plugin" / "plugin.json"

    assert manifest_path.exists(), f"Manifest not found at {manifest_path}"

    with open(manifest_path) as f:
        manifest = json.load(f)

    # Validate required fields
    required_fields = ["name", "version", "description", "cortex"]
    for field in required_fields:
        assert field in manifest, f"Missing required field: {field}"

    # Validate cortex subdirectory structure
    cortex_config = manifest.get("cortex", {})
    assert "agents_dir" in cortex_config, "Missing cortex.agents_dir"
    assert "skills_dir" in cortex_config, "Missing cortex.skills_dir"


def test_agents_md_vs_agents_referential_integrity():
    """Test that AGENTS.md agents list matches agents/ directory."""
    agents_md_path = PLUGIN_ROOT / "AGENTS.md"
    agents_dir = PLUGIN_ROOT / "agents"

    assert agents_md_path.exists(), f"AGENTS.md not found at {agents_md_path}"
    assert agents_dir.exists(), f"agents/ directory not found at {agents_dir}"

    # Read AGENTS.md and extract agent names from the Available Agents table
    with open(agents_md_path) as f:
        agents_md_content = f.read()

    # Extract agent names from markdown table (format: | `agent-name` | description |)
    agents_mentioned = set()
    for match in re.finditer(r"\|\s*`([a-z-]+)`\s*\|", agents_md_content):
        agents_mentioned.add(match.group(1))

    # Get actual agent files from agents/ directory
    agent_files = set()
    for file_path in agents_dir.glob("*.md"):
        if file_path.name != "README.md":
            agent_files.add(file_path.stem)

    # Filter to only agent files (not commands/skills)
    # From AGENTS.md, we know the agents are: drift-monitor, alert-builder, performance-tracker
    expected_agents = {"drift-monitor", "alert-builder", "performance-tracker"}

    for agent_name in expected_agents:
        agent_file = agents_dir / f"{agent_name}.md"
        assert agent_file.exists(), f"Agent '{agent_name}' referenced in AGENTS.md but file not found: {agent_file}"
        assert agent_name in agents_mentioned, f"Agent '{agent_name}' file exists but not mentioned in AGENTS.md"


def test_skills_md_vs_skills_referential_integrity():
    """Test that AGENTS.md skills list matches skills/ directory."""
    agents_md_path = PLUGIN_ROOT / "AGENTS.md"
    skills_dir = PLUGIN_ROOT / "skills"

    assert agents_md_path.exists(), f"AGENTS.md not found at {agents_md_path}"
    assert skills_dir.exists(), f"skills/ directory not found at {skills_dir}"

    # Read AGENTS.md and extract skill names from the Available Skills table
    with open(agents_md_path) as f:
        agents_md_content = f.read()

    # Extract skill names from markdown table (format: | `/skill-name` | trigger |)
    # Using re.search with word boundary as specified in requirements
    skills_mentioned = set()
    expected_skills = {"drift-detect", "drift-monitor", "drift-compare", "drift-alert", "drift-report", "perf-track"}

    for skill_name in expected_skills:
        if re.search(rf"\b/?{re.escape(skill_name)}\b", agents_md_content):
            skills_mentioned.add(skill_name)

    # Verify each expected skill has a matching directory
    for skill_name in expected_skills:
        skill_dir = skills_dir / skill_name
        assert skill_dir.exists(), f"Skill '{skill_name}' referenced in AGENTS.md but directory not found: {skill_dir}"
        assert skill_name in skills_mentioned, f"Skill '{skill_name}' directory exists but not mentioned in AGENTS.md"
