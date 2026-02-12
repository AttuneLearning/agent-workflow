#!/usr/bin/env python3
"""
Install Codex workflow skills with an active team profile.

Usage examples:
  python3 .codex-workflow/scripts/install_team.py --list-teams
  python3 .codex-workflow/scripts/install_team.py --team backend
  python3 .codex-workflow/scripts/install_team.py --team data-warehousing --target /tmp/codex-skills --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _load_profiles(profiles_path: Path) -> Dict[str, Any]:
  if not profiles_path.exists():
    raise FileNotFoundError(f"Missing team profiles: {profiles_path}")
  with profiles_path.open("r", encoding="utf-8") as f:
    return json.load(f)


def _default_target(pack_name: str) -> Path:
  codex_home = os.environ.get("CODEX_HOME")
  if codex_home:
    return Path(codex_home).expanduser() / "skills" / pack_name
  return Path.home() / ".codex" / "skills" / pack_name


def _print_teams(profiles: Dict[str, Any]) -> None:
  teams = profiles.get("teams", {})
  if not teams:
    print("No teams found in profiles.")
    return
  print("Available teams:")
  for team_id in sorted(teams.keys()):
    team = teams[team_id]
    name = team.get("name", team_id)
    alias = team.get("alias", "-")
    prefix = team.get("issue_prefix", "-")
    print(f"  - {team_id:16} name={name}, alias={alias}, issue_prefix={prefix}")


def _copy_skills(workflow_root: Path, target_root: Path, enabled_skills: list[str], dry_run: bool) -> None:
  target_skills = target_root / "skills"
  if dry_run:
    print(f"[dry-run] mkdir -p {target_skills}")
  else:
    target_skills.mkdir(parents=True, exist_ok=True)

  for skill in enabled_skills:
    src = workflow_root / "skills" / skill
    dst = target_skills / skill
    if not src.exists():
      raise FileNotFoundError(f"Skill folder not found: {src}")
    if dry_run:
      print(f"[dry-run] copytree {src} -> {dst}")
      continue
    shutil.copytree(src, dst, dirs_exist_ok=True)


def _copy_team_metadata(workflow_root: Path, target_root: Path, dry_run: bool) -> None:
  src_teams = workflow_root / "teams"
  dst_teams = target_root / "teams"
  if dry_run:
    print(f"[dry-run] copytree {src_teams} -> {dst_teams}")
    return
  shutil.copytree(src_teams, dst_teams, dirs_exist_ok=True)


def _write_json(path: Path, payload: Dict[str, Any], dry_run: bool) -> None:
  if dry_run:
    print(f"[dry-run] write {path}")
    return
  path.parent.mkdir(parents=True, exist_ok=True)
  with path.open("w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
    f.write("\n")


def _write_text_if_missing(path: Path, content: str, dry_run: bool) -> None:
  if path.exists():
    return
  if dry_run:
    print(f"[dry-run] write {path}")
    return
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(content, encoding="utf-8")


def _append_line_if_missing(path: Path, line: str, dry_run: bool) -> None:
  if not path.exists():
    _write_text_if_missing(path, f"{line}\n", dry_run)
    return
  existing = path.read_text(encoding="utf-8")
  if line in existing:
    return
  if dry_run:
    print(f"[dry-run] append line to {path}: {line}")
    return
  with path.open("a", encoding="utf-8") as f:
    if not existing.endswith("\n"):
      f.write("\n")
    f.write(f"{line}\n")


def _write_team_profile_md(path: Path, team_id: str, team: Dict[str, Any], dry_run: bool) -> None:
  lines = [
    f"# Active Team Profile: {team_id}",
    "",
    f"- Name: {team.get('name', team_id)}",
    f"- Alias: {team.get('alias', '-')}",
    f"- Issue Prefix: {team.get('issue_prefix', '-')}",
    "",
    "## Enabled Skills",
  ]
  for skill in team.get("enabled_skills", []):
    lines.append(f"- `{skill}`")
  lines.append("")
  lines.append("## Default Paths")
  for key, value in sorted(team.get("default_paths", {}).items()):
    lines.append(f"- `{key}`: `{value}`")
  lines.append("")
  body = "\n".join(lines) + "\n"

  if dry_run:
    print(f"[dry-run] write {path}")
    return
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(body, encoding="utf-8")


def _ensure_ai_team_store(
  project_root: Path,
  team_id: str,
  enabled_skills: list[str],
  dry_run: bool
) -> Dict[str, str]:
  ai_root = project_root / "ai_team_config"
  shared_memory_root = ai_root / "memory_store"
  team_root = ai_root / team_id
  adr_store = team_root / "adr_store"
  memory_store = team_root / "memory_store"
  context_store = team_root / "context_store"
  skill_store_root = team_root / "skill_store"

  dirs = [ai_root, shared_memory_root, team_root, adr_store, memory_store, context_store, skill_store_root]
  for directory in dirs:
    if directory.exists():
      continue
    if dry_run:
      print(f"[dry-run] mkdir -p {directory}")
    else:
      directory.mkdir(parents=True, exist_ok=True)

  # Root vault index
  root_index = ai_root / "index.md"
  root_index_content = (
    "# AI Team Config Vault\n\n"
    "This is the shared team-oriented AI storage vault in Obsidian-compatible Markdown.\n\n"
    "## Shared Stores\n"
    "- Shared Memory: [[ai_team_config/memory_store/index]]\n\n"
    "## Team Roots\n"
    f"- [[ai_team_config/{team_id}/index]]\n\n"
    "## Notes\n"
    "- Use wiki links for cross-reference and backlinks.\n"
    "- Keep skill memory in `skill_store/<skill>/memory_store/`.\n"
  )
  _write_text_if_missing(root_index, root_index_content, dry_run)
  _append_line_if_missing(root_index, "- Shared Memory: [[ai_team_config/memory_store/index]]", dry_run)
  _append_line_if_missing(root_index, f"- [[ai_team_config/{team_id}/index]]", dry_run)

  shared_memory_index = shared_memory_root / "index.md"
  _write_text_if_missing(
    shared_memory_index,
    (
      "# Shared Memory Store\n\n"
      "Backlinks: [[ai_team_config/index]] [[TEAM_CONFIG_CONTRACT]]\n\n"
      "This vault stores shared cross-team memory artifacts in Obsidian-compatible Markdown.\n"
    ),
    dry_run
  )

  # Team index with cross-links
  team_index = team_root / "index.md"
  team_index_content = (
    f"# Team Vault: {team_id}\n\n"
    f"Backlink: [[ai_team_config/index]]\n\n"
    "## Core Stores\n"
    f"- ADR: [[ai_team_config/{team_id}/adr_store/index]]\n"
    f"- Memory: [[ai_team_config/{team_id}/memory_store/index]]\n"
    f"- Context: [[ai_team_config/{team_id}/context_store/index]]\n"
    f"- Skill Store: [[ai_team_config/{team_id}/skill_store/index]]\n"
  )
  _write_text_if_missing(team_index, team_index_content, dry_run)

  adr_index = adr_store / "index.md"
  _write_text_if_missing(
    adr_index,
    (
      "# ADR Store\n\n"
      f"Backlinks: [[ai_team_config/{team_id}/index]] [[ai_team_config/index]]\n\n"
      "Store architecture notes, ADR drafts, and decision snapshots here.\n"
    ),
    dry_run
  )

  memory_index = memory_store / "index.md"
  _write_text_if_missing(
    memory_index,
    (
      "# Memory Store\n\n"
      f"Backlinks: [[ai_team_config/{team_id}/index]] [[ai_team_config/index]]\n\n"
      "Store long-lived team memory and distilled implementation notes here.\n"
    ),
    dry_run
  )

  context_index = context_store / "index.md"
  _write_text_if_missing(
    context_index,
    (
      "# Context Store\n\n"
      f"Backlinks: [[ai_team_config/{team_id}/index]] [[ai_team_config/index]]\n\n"
      "Store pre-implementation context packs and topic context notes here.\n"
    ),
    dry_run
  )

  skill_store_index = skill_store_root / "index.md"
  skill_store_index_content = (
    "# Skill Store\n\n"
    f"Backlinks: [[ai_team_config/{team_id}/index]] [[ai_team_config/index]]\n\n"
    "## Skill Memory Stores\n"
  )
  for skill in enabled_skills:
    skill_store_index_content += f"- [[ai_team_config/{team_id}/skill_store/{skill}/memory_store/index]]\n"
  _write_text_if_missing(skill_store_index, skill_store_index_content, dry_run)

  for skill in enabled_skills:
    skill_memory_dir = skill_store_root / skill / "memory_store"
    if not skill_memory_dir.exists():
      if dry_run:
        print(f"[dry-run] mkdir -p {skill_memory_dir}")
      else:
        skill_memory_dir.mkdir(parents=True, exist_ok=True)

    skill_memory_index = skill_memory_dir / "index.md"
    _write_text_if_missing(
      skill_memory_index,
      (
        f"# Skill Memory: {skill}\n\n"
        f"Backlinks: [[ai_team_config/{team_id}/skill_store/index]] "
        f"[[ai_team_config/{team_id}/memory_store/index]] [[ai_team_config/{team_id}/index]]\n\n"
        "Store skill-specific memory notes in this folder.\n"
      ),
      dry_run
    )

  return {
    "vault_root": str(ai_root),
    "shared_memory_root": str(shared_memory_root),
    "team_root": str(team_root),
    "adr_store": str(adr_store),
    "memory_store": str(memory_store),
    "context_store": str(context_store),
    "skill_store_root": str(skill_store_root)
  }


def _ensure_team_contract(project_root: Path, dry_run: bool) -> None:
  contract_path = project_root / "TEAM_CONFIG_CONTRACT.md"
  contract_content = (
    "# Team Config Contract\n\n"
    "This file defines how team-scoped AI storage is organized for the project.\n\n"
    "Required shared vault structure:\n"
    "- `ai_team_config/memory_store/`\n\n"
    "Required team vault structure:\n"
    "- `ai_team_config/<team>/adr_store/`\n"
    "- `ai_team_config/<team>/memory_store/`\n"
    "- `ai_team_config/<team>/context_store/`\n"
    "- `ai_team_config/<team>/skill_store/<skill>/memory_store/`\n\n"
    "Storage format: Obsidian-compatible Markdown with wiki-links/backlinks.\n"
  )
  _write_text_if_missing(contract_path, contract_content, dry_run)


def main() -> int:
  parser = argparse.ArgumentParser(description="Install Codex workflow with team-specific profile")
  parser.add_argument("--team", help="Team id, e.g. backend, frontend, data-warehousing")
  parser.add_argument("--list-teams", action="store_true", help="List available team ids")
  parser.add_argument("--target", help="Install destination (default: $CODEX_HOME/skills/codex-workflow or ~/.codex/skills/codex-workflow)")
  parser.add_argument("--pack-name", default="codex-workflow", help="Pack name under skills directory (default: codex-workflow)")
  parser.add_argument("--workspace-root", help="Project root (default: parent of .codex-workflow)")
  parser.add_argument("--force", action="store_true", help="Overwrite existing target directory")
  parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
  parser.add_argument("--no-local-config", action="store_true", help="Do not write .codex-workflow/config/active-team.json")
  args = parser.parse_args()

  workflow_root = Path(__file__).resolve().parents[1]
  project_root = Path(args.workspace_root).resolve() if args.workspace_root else workflow_root.parent
  profiles_path = workflow_root / "teams" / "profiles.json"
  profiles = _load_profiles(profiles_path)
  teams = profiles.get("teams", {})

  if args.list_teams:
    _print_teams(profiles)
    return 0

  if not args.team:
    parser.error("--team is required unless --list-teams is used")

  if args.team not in teams:
    print(f"Unknown team: {args.team}", file=sys.stderr)
    _print_teams(profiles)
    return 2

  target_root = Path(args.target).expanduser() if args.target else _default_target(args.pack_name)
  team_profile = teams[args.team]

  if target_root.exists():
    if not args.force:
      print(
        f"Target exists: {target_root}\n"
        "Use --force to replace, or pass --target to install elsewhere.",
        file=sys.stderr,
      )
      return 3
    if args.dry_run:
      print(f"[dry-run] rm -rf {target_root}")
    else:
      shutil.rmtree(target_root)

  if args.dry_run:
    print(f"[dry-run] mkdir -p {target_root}")
  else:
    target_root.mkdir(parents=True, exist_ok=True)

  enabled_skills = team_profile.get("enabled_skills", [])
  _copy_skills(workflow_root, target_root, enabled_skills, args.dry_run)
  _copy_team_metadata(workflow_root, target_root, args.dry_run)
  _ensure_team_contract(project_root, args.dry_run)
  team_store_paths = _ensure_ai_team_store(project_root, args.team, enabled_skills, args.dry_run)

  installed_at = datetime.now(timezone.utc).isoformat()
  team_profile_with_store = dict(team_profile)
  default_paths = dict(team_profile_with_store.get("default_paths", {}))
  default_paths.update({
    "memory_root": team_store_paths["shared_memory_root"],
    "team_vault_root": team_store_paths["team_root"],
    "adr_store": team_store_paths["adr_store"],
    "memory_store": team_store_paths["memory_store"],
    "context_store": team_store_paths["context_store"],
    "skill_store_root": team_store_paths["skill_store_root"]
  })
  team_profile_with_store["default_paths"] = default_paths

  manifest = {
    "pack_name": args.pack_name,
    "installed_at": installed_at,
    "team_id": args.team,
    "team_profile": team_profile_with_store,
    "team_store_paths": team_store_paths,
    "source_workflow_root": str(workflow_root),
    "project_root": str(project_root),
  }

  _write_json(target_root / "config" / "active-team.json", manifest, args.dry_run)
  _write_json(target_root / "install-manifest.json", manifest, args.dry_run)
  _write_team_profile_md(target_root / "TEAM_PROFILE.md", args.team, team_profile, args.dry_run)

  if not args.no_local_config:
    _write_json(workflow_root / "config" / "active-team.json", manifest, args.dry_run)

  print("Installation complete." if not args.dry_run else "Dry-run complete.")
  print(f"Team: {args.team}")
  print(f"Target: {target_root}")
  if args.no_local_config:
    print("Local config: skipped (--no-local-config)")
  else:
    print(f"Local config: {workflow_root / 'config' / 'active-team.json'}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
