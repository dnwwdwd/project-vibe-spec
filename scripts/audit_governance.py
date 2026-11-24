#!/usr/bin/env python3
"""Read-only governance auditor for repositories using project-vibe-spec.

Uses Python standard library only. Never modifies files in the target repository.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    "vendor",
    ".cache",
}

ROOT_INSTRUCTION_CANDIDATES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".cursorrules",
    ".github/copilot-instructions.md",
    "GEMINI.md",
)

DOC_MAP_CANDIDATES = (
    "DOCUMENT_MAP.md",
    "docs/DOCUMENT_MAP.md",
)

VALID_MAP_STATUSES = {"现行", "参考", "待澄清", "缺失", "不适用"}

ROUTE_START = "<!-- project-vibe-spec:routes:start -->"
ROUTE_END = "<!-- project-vibe-spec:routes:end -->"

LEDGER_DOMAIN_SPECS = (
    (
        "Requirements",
        ("Requirements", "requirements", "docs/Requirements", "docs/requirements"),
        re.compile(r"^REQ-.*\.md$", re.IGNORECASE),
    ),
    (
        "Decisions",
        ("Decisions", "decisions", "docs/Decisions", "docs/decisions"),
        re.compile(r"^DEC-.*\.md$", re.IGNORECASE),
    ),
    (
        "Progress",
        ("Progress", "progress", "docs/Progress", "docs/progress"),
        re.compile(r"^PROG-.*\.md$", re.IGNORECASE),
    ),
)

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
CODE_SPAN_RE = re.compile(r"`([^`]+)`")
PLACEHOLDER_RE = re.compile(r"<[^>]+>")
PATH_LIKE_RE = re.compile(
    r"^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*(?:\.[A-Za-z0-9_-]+|/)$"
)
MD_FILE_REF_RE = re.compile(
    r"(?<![A-Za-z0-9_/-])([A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*\.md)(?:#[^\s|)`]*)?"
)


def rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def resolve_local_path(raw: str, repo_root: Path, base_dir: Path) -> Path | None:
    cleaned = raw.strip().strip("`").strip()
    if not cleaned:
        return None
    if cleaned.startswith(("http://", "https://", "mailto:", "#")):
        return None
    if PLACEHOLDER_RE.search(cleaned):
        return None
    cleaned = cleaned.split("#", 1)[0].strip()
    if not cleaned:
        return None
    # Strip surrounding quotes if present
    cleaned = cleaned.strip("'\"")
    candidates = [repo_root / cleaned, base_dir / cleaned]
    for cand in candidates:
        if cand.exists():
            return cand
    return None


def looks_like_path(token: str) -> bool:
    token = token.strip()
    if not token or token.startswith(("http://", "https://", "#")):
        return False
    if PLACEHOLDER_RE.search(token):
        return False
    token_no_anchor = token.split("#", 1)[0]
    if not token_no_anchor:
        return False
    if "/" in token_no_anchor or token_no_anchor.endswith(".md"):
        return bool(PATH_LIKE_RE.match(token_no_anchor))
    return False


def parse_markdown_tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    lines = text.splitlines()
    tables: list[tuple[list[str], list[list[str]]]] = []
    i = 0
    while i < len(lines) - 1:
        line = lines[i].strip()
        next_line = lines[i + 1].strip()
        if (
            line.startswith("|")
            and next_line.startswith("|")
            and re.match(r"^\|[\s:|-]+\|?$", next_line)
        ):
            headers = [c.strip() for c in line.strip("|").split("|")]
            rows: list[list[str]] = []
            j = i + 2
            while j < len(lines):
                row_line = lines[j].strip()
                if not row_line.startswith("|"):
                    break
                cells = [c.strip() for c in row_line.strip("|").split("|")]
                if any(cells):
                    rows.append(cells)
                j += 1
            tables.append((headers, rows))
            i = j
        else:
            i += 1
    return tables


def audit_instruction_files(
    repo_root: Path, max_agents_lines: int
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    root_files: list[dict[str, Any]] = []
    for rel in ROOT_INSTRUCTION_CANDIDATES:
        p = repo_root / rel
        if p.is_file():
            content = read_text_safe(p)
            line_count = len(content.splitlines())
            root_files.append({"path": rel, "lines": line_count})

    nested_files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        current = Path(dirpath)
        if current == repo_root:
            continue
        for fname in ("AGENTS.md", "CLAUDE.md"):
            if fname in filenames:
                nested_files.append(rel_posix(current / fname, repo_root))

    substantive_roots = [f for f in root_files if f["lines"] > 15]
    if len(substantive_roots) > 1:
        names = ", ".join(f"{f['path']}({f['lines']}行)" for f in substantive_roots)
        warnings.append(
            f"检测到多个内容较完整的根指令文件，存在平行规则漂移风险：{names}"
        )

    routes_info: dict[str, Any] = {
        "has_agents_md": False,
        "has_route_markers": False,
        "broken_route_paths": [],
        "placeholders_found": [],
    }

    agents_path = repo_root / "AGENTS.md"
    if agents_path.is_file():
        routes_info["has_agents_md"] = True
        content = read_text_safe(agents_path)
        lines = content.splitlines()
        if len(lines) > max_agents_lines:
            warnings.append(
                f"根 AGENTS.md 共 {len(lines)} 行，超过阈值 {max_agents_lines} 行，建议检查是否混入事实文档正文或过细规则"
            )

        has_start = ROUTE_START in content
        has_end = ROUTE_END in content
        if has_start ^ has_end:
            errors.append("根 AGENTS.md 中的路由标记未成对出现（缺少 start 或 end）")
        elif has_start and has_end:
            start_idx = content.index(ROUTE_START)
            end_idx = content.index(ROUTE_END)
            if end_idx < start_idx:
                errors.append("根 AGENTS.md 中的路由标记顺序颠倒（end 在 start 之前）")
            else:
                routes_info["has_route_markers"] = True
                block = content[start_idx + len(ROUTE_START) : end_idx]
                for b_line in block.splitlines():
                    stripped = b_line.strip()
                    if not stripped or stripped.startswith(">"):
                        continue
                    for ph in PLACEHOLDER_RE.findall(stripped):
                        routes_info["placeholders_found"].append(ph)
                    if "缺失" in stripped or "不适用" in stripped:
                        continue
                    refs: list[str] = []
                    for m in MD_LINK_RE.findall(stripped):
                        refs.append(m.strip())
                    for code in CODE_SPAN_RE.findall(stripped):
                        if looks_like_path(code):
                            refs.append(code.strip())
                    for ref in dict.fromkeys(refs):
                        if ref.startswith(("http://", "https://", "#")):
                            continue
                        if PLACEHOLDER_RE.search(ref):
                            continue
                        if resolve_local_path(ref, repo_root, repo_root) is None:
                            routes_info["broken_route_paths"].append(ref)
                            errors.append(f"AGENTS.md 路由块指向不存在的路径：`{ref}`")
                if routes_info["placeholders_found"]:
                    unique_ph = ", ".join(dict.fromkeys(routes_info["placeholders_found"]))
                    warnings.append(
                        f"AGENTS.md 路由块中仍有未替换占位符：{unique_ph}"
                    )
    else:
        warnings.append("仓库根目录未发现 AGENTS.md")

    return (
        {
            "root_instruction_files": root_files,
            "nested_instruction_files": sorted(nested_files),
            "routes": routes_info,
        },
        errors,
        warnings,
    )


def extract_paths_from_cell(cell: str) -> list[str]:
    cell = cell.strip()
    if not cell or cell in {"-", "—", "无", "N/A", "n/a"}:
        return []
    found: list[str] = []
    for target in MD_LINK_RE.findall(cell):
        t = target.strip()
        if t and not t.startswith(("http://", "https://", "#")):
            found.append(t)
    if found:
        return list(dict.fromkeys(found))
    for code in CODE_SPAN_RE.findall(cell):
        c = code.strip()
        if c and c not in {"-", "—", "无"}:
            found.append(c)
    if found:
        return list(dict.fromkeys(found))
    # Fallback: split plain cell on commas / Chinese commas / semicolons
    parts = re.split(r"[,，;；]\s*", cell)
    for part in parts:
        p = part.strip()
        if p and p not in {"-", "—", "无"} and looks_like_path(p):
            found.append(p)
    return list(dict.fromkeys(found))


def audit_document_map(
    repo_root: Path,
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    map_path: Path | None = None
    for cand in DOC_MAP_CANDIDATES:
        p = repo_root / cand
        if p.is_file():
            map_path = p
            break

    if map_path is None:
        warnings.append("未发现 DOCUMENT_MAP.md（或 docs/DOCUMENT_MAP.md）")
        return {"path": None, "status_counts": {}, "entries": []}, errors, warnings

    text = read_text_safe(map_path)
    tables = parse_markdown_tables(text)
    target_table = None
    for headers, rows in tables:
        joined = " ".join(headers)
        if "职责" in joined and "状态" in joined:
            target_table = (headers, rows)
            break

    if target_table is None:
        warnings.append(f"{rel_posix(map_path, repo_root)} 中未解析到包含“职责/状态”的映射表")
        return {
            "path": rel_posix(map_path, repo_root),
            "status_counts": {},
            "entries": [],
        }, errors, warnings

    headers, rows = target_table

    def find_col(keywords: tuple[str, ...]) -> int | None:
        for idx, h in enumerate(headers):
            if any(k in h for k in keywords):
                return idx
        return None

    role_idx = find_col(("职责",))
    status_idx = find_col(("状态",))
    path_idx = find_col(("实际路径", "路径", "位置"))

    status_counts: dict[str, int] = {}
    active_by_role: dict[str, list[str]] = {}
    entries: list[dict[str, Any]] = []
    clarify_roles: list[str] = []

    for row in rows:
        role = row[role_idx].strip() if role_idx is not None and role_idx < len(row) else ""
        status = (
            row[status_idx].strip().strip("`")
            if status_idx is not None and status_idx < len(row)
            else ""
        )
        raw_path = (
            row[path_idx].strip() if path_idx is not None and path_idx < len(row) else ""
        )
        if not role and not status:
            continue

        status_counts[status] = status_counts.get(status, 0) + 1
        paths = extract_paths_from_cell(raw_path)
        entries.append(
            {"role": role, "status": status, "raw_path": raw_path, "paths": paths}
        )

        if status not in VALID_MAP_STATUSES:
            errors.append(
                f"{rel_posix(map_path, repo_root)} 中职责「{role}」使用了未定义状态：`{status}`"
            )
            continue

        if status == "待澄清":
            clarify_roles.append(role)

        if status == "现行":
            active_by_role.setdefault(role, []).append(raw_path)

        if status in {"现行", "参考"}:
            if not paths:
                errors.append(
                    f"{rel_posix(map_path, repo_root)} 中「{role}」状态为 `{status}`，但未填写有效路径"
                )
            else:
                for p_str in paths:
                    if resolve_local_path(p_str, repo_root, map_path.parent) is None:
                        errors.append(
                            f"{rel_posix(map_path, repo_root)} 中「{role}」指向不存在的路径：`{p_str}`"
                        )

    for role, r_paths in active_by_role.items():
        if len(r_paths) > 1:
            errors.append(
                f"{rel_posix(map_path, repo_root)} 中职责「{role}」出现 {len(r_paths)} 个 `现行` 正本"
            )

    return (
        {
            "path": rel_posix(map_path, repo_root),
            "status_counts": status_counts,
            "clarify_roles": clarify_roles,
            "entry_count": len(entries),
        },
        errors,
        warnings,
    )


def audit_ledgers_and_records(
    repo_root: Path,
) -> tuple[dict[str, Any], list[str], list[str], list[Path]]:
    errors: list[str] = []
    warnings: list[str] = []
    domains_report: dict[str, Any] = {}
    discovered_files: list[Path] = []

    for domain_name, candidates, record_pattern in LEDGER_DOMAIN_SPECS:
        found_dir: Path | None = None
        for cand in candidates:
            p = repo_root / cand
            if p.is_dir():
                found_dir = p
                break
        if found_dir is None:
            continue

        ledger_path: Path | None = None
        record_files: list[Path] = []
        for child in sorted(found_dir.iterdir()):
            if not child.is_file() or child.name.endswith(".template"):
                continue
            if child.name.lower() == "ledger.md":
                ledger_path = child
                discovered_files.append(child)
            elif record_pattern.match(child.name):
                record_files.append(child)
                discovered_files.append(child)

        broken_links: list[str] = []
        orphan_records: list[str] = []

        if ledger_path is not None:
            ledger_text = read_text_safe(ledger_path)
            # Check explicit markdown links and .md path references inside table rows
            referenced_paths: set[str] = set()
            for _, rows in parse_markdown_tables(ledger_text):
                for row in rows:
                    row_joined = " | ".join(row)
                    for target in MD_LINK_RE.findall(row_joined):
                        t = target.strip()
                        if t.startswith(("http://", "https://", "#")) or PLACEHOLDER_RE.search(t):
                            continue
                        referenced_paths.add(t)
                    for m in MD_FILE_REF_RE.findall(row_joined):
                        if PLACEHOLDER_RE.search(m):
                            continue
                        referenced_paths.add(m)

            for ref in sorted(referenced_paths):
                resolved = resolve_local_path(ref, repo_root, found_dir)
                if resolved is None:
                    broken_links.append(ref)
                    errors.append(
                        f"{rel_posix(ledger_path, repo_root)} 引用了不存在的文件：`{ref}`"
                    )

            for rec in record_files:
                rec_rel_root = rel_posix(rec, repo_root)
                if rec.name not in ledger_text and rec_rel_root not in ledger_text:
                    orphan_records.append(rec_rel_root)
                    warnings.append(
                        f"记录文件 `{rec_rel_root}` 未在 `{rel_posix(ledger_path, repo_root)}` 中登记"
                    )
        elif record_files:
            warnings.append(
                f"目录 `{rel_posix(found_dir, repo_root)}` 包含 {len(record_files)} 个记录文件，但缺少 LEDGER.md"
            )

        domains_report[domain_name] = {
            "dir": rel_posix(found_dir, repo_root),
            "ledger": rel_posix(ledger_path, repo_root) if ledger_path else None,
            "record_count": len(record_files),
            "broken_links": broken_links,
            "orphan_records": orphan_records,
        }

    return domains_report, errors, warnings, discovered_files


def scan_pending_items(repo_root: Path, governance_files: list[Path]) -> dict[str, list[str]]:
    extra_candidates = (
        "BUG_TRACKER.md",
        "docs/BUG_TRACKER.md",
        "PROGRESS.md",
        "docs/PROGRESS.md",
    )
    scan_paths: list[Path] = list(governance_files)
    seen = {p.resolve() for p in scan_paths}
    for cand in extra_candidates:
        p = repo_root / cand
        if p.is_file() and p.resolve() not in seen:
            scan_paths.append(p)
            seen.add(p.resolve())

    pending_decisions: list[str] = []
    pending_regressions: list[str] = []

    empty_values = {"", "无", "无。", "-", "—", "none", "n/a"}

    for path in sorted(scan_paths):
        rel = rel_posix(path, repo_root)
        text = read_text_safe(path)
        is_ledger = path.name.lower() == "ledger.md"

        if is_ledger:
            for headers, rows in parse_markdown_tables(text):
                status_col = next(
                    (i for i, h in enumerate(headers) if "状态" in h), None
                )
                id_col = next((i for i, h in enumerate(headers) if "ID" in h.upper()), 0)
                if status_col is None:
                    continue
                for row in rows:
                    if status_col < len(row) and row[status_col].strip().strip("`") == "待方案确认":
                        item_id = row[id_col].strip() if id_col < len(row) else rel
                        pending_decisions.append(f"{rel} ({item_id})")
        else:
            for line_no, raw_line in enumerate(text.splitlines(), start=1):
                line = raw_line.strip()
                if re.match(r"^[-*>]\s*状态[：:]\s*`?待方案确认`?$", line):
                    pending_decisions.append(f"{rel}:{line_no}")
                m = re.match(r"^[-*]\s*待实机回归[：:]\s*(.*)$", line)
                if m:
                    val = m.group(1).strip()
                    if val.lower() not in empty_values and not PLACEHOLDER_RE.search(val):
                        pending_regressions.append(f"{rel}:{line_no} — {val}")

    return {
        "pending_decisions": list(dict.fromkeys(pending_decisions)),
        "pending_real_device_regressions": list(dict.fromkeys(pending_regressions)),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Governance Audit: `{report['repo']}`")
    lines.append("")

    inst = report["instruction_files"]
    roots = inst["root_instruction_files"]
    root_desc = (
        ", ".join(f"`{r['path']}` ({r['lines']}行)" for r in roots)
        if roots
        else "无"
    )
    lines.append("## 1. 指令文件与路由")
    lines.append(f"- 根指令文件：{root_desc}")
    nested = inst["nested_instruction_files"]
    lines.append(
        f"- 嵌套指令文件：{', '.join(f'`{p}`' for p in nested) if nested else '无'}"
    )
    routes = inst["routes"]
    lines.append(
        f"- `AGENTS.md` 路由标记：{'已配置' if routes['has_route_markers'] else '未配置'}"
    )

    lines.append("")
    lines.append("## 2. 文档地图")
    dmap = report["document_map"]
    if dmap["path"]:
        counts = ", ".join(f"{k}:{v}" for k, v in dmap["status_counts"].items()) or "无条目"
        lines.append(f"- 路径：`{dmap['path']}`（{counts}）")
        if dmap.get("clarify_roles"):
            lines.append(f"- 待澄清职责：{', '.join(dmap['clarify_roles'])}")
    else:
        lines.append("- 未发现 `DOCUMENT_MAP.md`")

    lines.append("")
    lines.append("## 3. 交付台账")
    ledgers = report["ledgers"]
    if ledgers:
        for name, info in ledgers.items():
            ledger_str = f"`{info['ledger']}`" if info["ledger"] else "缺失 LEDGER.md"
            lines.append(
                f"- {name} (`{info['dir']}`): {ledger_str}，记录文件 {info['record_count']} 个"
            )
    else:
        lines.append("- 未发现 Requirements / Decisions / Progress 目录")

    pending = report["pending"]
    if pending["pending_decisions"] or pending["pending_real_device_regressions"]:
        lines.append("")
        lines.append("## 4. 未收口事项")
        if pending["pending_decisions"]:
            lines.append("- 待方案确认：")
            for item in pending["pending_decisions"]:
                lines.append(f"  - {item}")
        if pending["pending_real_device_regressions"]:
            lines.append("- 待实机回归：")
            for item in pending["pending_real_device_regressions"]:
                lines.append(f"  - {item}")

    lines.append("")
    lines.append(
        f"## 结论：Errors {len(report['errors'])} / Warnings {len(report['warnings'])}"
    )
    if report["errors"]:
        lines.append("### Errors")
        for err in report["errors"]:
            lines.append(f"- [ERROR] {err}")
    if report["warnings"]:
        lines.append("### Warnings")
        for warn in report["warnings"]:
            lines.append(f"- [WARN] {warn}")
    if not report["errors"] and not report["warnings"]:
        lines.append("- 未发现结构性错误或告警。")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only audit for project-vibe-spec governance files."
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Path to the target repository (default: current directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON report.",
    )
    parser.add_argument(
        "--max-agents-lines",
        type=int,
        default=150,
        help="Warn if root AGENTS.md exceeds this line count (default: 150).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any errors are found.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    if not repo_root.is_dir():
        print(f"Error: target path is not a directory: {args.repo}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    inst_report, inst_err, inst_warn = audit_instruction_files(
        repo_root, args.max_agents_lines
    )
    errors.extend(inst_err)
    warnings.extend(inst_warn)

    dmap_report, dmap_err, dmap_warn = audit_document_map(repo_root)
    errors.extend(dmap_err)
    warnings.extend(dmap_warn)

    ledger_report, ledger_err, ledger_warn, gov_files = audit_ledgers_and_records(
        repo_root
    )
    errors.extend(ledger_err)
    warnings.extend(ledger_warn)

    pending_report = scan_pending_items(repo_root, gov_files)

    report = {
        "repo": str(repo_root),
        "instruction_files": inst_report,
        "document_map": dmap_report,
        "ledgers": ledger_report,
        "pending": pending_report,
        "errors": errors,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))

    if args.strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
