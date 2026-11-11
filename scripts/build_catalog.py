#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
REF = os.environ.get("CATALOG_REF", "main")


def frontmatter(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path}: missing YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: unterminated YAML frontmatter") from exc

    fields = {}
    index = 1
    while index < end:
        match = re.match(r"^([a-zA-Z0-9_-]+):(?:\s+(.*))?$", lines[index])
        if not match:
            index += 1
            continue
        key, value = match.groups()
        value = value or ""
        if value in (">", ">-", "|", "|-"):
            index += 1
            parts = []
            while index < end and (not lines[index] or lines[index].startswith(" ")):
                if lines[index].strip():
                    parts.append(lines[index].strip())
                index += 1
            fields[key] = " ".join(parts)
            continue
        fields[key] = value.strip("\"'")
        index += 1
    return fields


def skill_categories():
    categories = {}
    in_skills = False
    category = None
    for line in (ROOT / "README.md").read_text(encoding="utf-8").splitlines():
        if line == "## Skills":
            in_skills = True
            continue
        if in_skills and line.startswith("## "):
            break
        if not in_skills:
            continue
        if line.startswith("### "):
            category = line.removeprefix("### ").strip()
            continue
        match = re.match(r"- \[`([^`]+)`\]\(skills/([^/]+)/[^)]+\)", line)
        if match:
            name, folder = match.groups()
            if name != folder or folder in categories:
                raise ValueError(f"README.md: invalid or duplicate skill entry {name}")
            categories[folder] = category
    return categories


def build():
    categories = skill_categories()
    ref = quote(REF, safe="/")
    source = "ragmha/rstack" if REF == "main" else f"https://github.com/ragmha/rstack/tree/{ref}"
    package = "github:ragmha/rstack" if REF == "main" else f"github:ragmha/rstack#{ref}"
    items = []
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        fields = frontmatter(path)
        name, description = fields.get("name"), fields.get("description")
        if name != path.parent.name or not description:
            raise ValueError(f"{path}: name must match folder and description is required")
        if name not in categories:
            raise ValueError(f"{name}: add it to a README.md skill category")
        items.append({
            "name": name,
            "category": categories[name],
            "description": description,
            "source": f"https://github.com/ragmha/rstack/blob/{ref}/{path.relative_to(ROOT).as_posix()}",
            "install": f"npx skills add {source} --skill {name}",
        })
    return {
        "ref": REF,
        "install": f"npx skills add {source}",
        "mcp": '{\n  "mcpServers": {\n    "rstack": %s\n  }\n}' % json.dumps({"command": "npx", "args": ["-y", package]}),
        "items": items,
    }


def main():
    parser = argparse.ArgumentParser(description="Build the rstack Pages catalog.")
    parser.add_argument("--check", action="store_true", help="fail if the generated catalog is stale")
    args = parser.parse_args()
    output = ROOT / "site" / "catalog.json"
    content = json.dumps(build(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != content:
            print(f"{output}: missing or stale; run python3 scripts/build_catalog.py", file=sys.stderr)
            return 1
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
