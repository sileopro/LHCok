#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每年 1 月 1 日（北京时间）归档：

1) 根目录开奖 txt → defaultData/
   保留已有年份，新年份写在最上面。

   格式示例：
     港彩 hk
     2026
     第001期：27 08 43 33 42 11 特码 29 牛
     ...

     2025
     第001期：09 23 42 44 45 46 特码 22 羊

   源文件 → defaultData：
     hk.txt   → defaultData/hk.txt   港彩 hk
     xam.txt  → defaultData/nz.txt   新澳 nz
     lam.txt  → defaultData/au.txt   老澳 au
     klb.txt  → defaultData/tw.txt   台彩 tw（若无则尝试 tc.txt）

2) 港彩月循：hkyxh.txt → hkwlyxh.txt（按年份）
   格式与日冲 hkwlrc 类似：
     2026
     08.11 → 087期: 13馬 → 猴鸡
     ...
     2025
     12.28 → 134期: 45雞 → 马羊
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

BJ = ZoneInfo("Asia/Shanghai")
ISSUE_RE = re.compile(r"第(\d{1,3})期")
YUEXUN_ISSUE_RE = re.compile(r"(\d{1,3})期")
YEAR_RE = re.compile(r"^\d{4}$")
LABEL_PREFIXES = ("港彩", "新澳", "老澳", "台彩")

ARCHIVES = [
    {"src": ["hk.txt"], "dest": "defaultData/hk.txt", "label": "港彩 hk"},
    {"src": ["xam.txt"], "dest": "defaultData/nz.txt", "label": "新澳 nz"},
    {"src": ["lam.txt"], "dest": "defaultData/au.txt", "label": "老澳 au"},
    {"src": ["klb.txt", "tc.txt"], "dest": "defaultData/tw.txt", "label": "台彩 tw"},
]

# 当年月循 → 往年月循（按年）
YUEXUN_SRC = "hkyxh.txt"
YUEXUN_DEST = "hkwlyxh.txt"
YUEXUN_DEST_LEGACY = "wlhkyxh.txt"  # 旧文件名，仅作读入兼容


def resolve_src(paths: list[str]) -> str | None:
    for name in paths:
        if os.path.isfile(name):
            return name
    return None


def is_label_line(line: str) -> bool:
    return any(line.startswith(p) for p in LABEL_PREFIXES)


def read_issue_lines(path: str) -> list[str]:
    """从根目录 txt 读取期数行（去掉标题行、年份行）。"""
    with open(path, encoding="utf-8") as f:
        lines = []
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if is_label_line(line):
                continue
            if YEAR_RE.fullmatch(line):
                continue
            if ISSUE_RE.search(line):
                lines.append(line)
        return lines


def sort_issue_lines(lines: list[str], reverse: bool = False) -> list[str]:
    def issue_num(line: str) -> int:
        m = ISSUE_RE.search(line) or YUEXUN_ISSUE_RE.search(line)
        return int(m.group(1)) if m else 0

    return sorted(lines, key=issue_num, reverse=reverse)


def parse_default_data(content: str) -> tuple[str | None, dict[int, list[str]]]:
    """解析 defaultData 多 year 块，返回 (彩种标题, {年: [期数行]})。"""
    label = None
    years: dict[int, list[str]] = {}
    current_year: int | None = None

    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            continue
        if label is None and is_label_line(line):
            label = line
            continue
        if YEAR_RE.fullmatch(line):
            current_year = int(line)
            years.setdefault(current_year, [])
            continue
        if current_year is not None and ISSUE_RE.search(line):
            years[current_year].append(line)

    return label, years


def build_multi_year_archive(label: str, year_blocks: dict[int, list[str]]) -> str:
    """按年份从新到旧输出，年份块之间空一行。"""
    parts = [label]
    sorted_years = sorted(year_blocks.keys(), reverse=True)
    for i, year in enumerate(sorted_years):
        lines = sort_issue_lines(year_blocks[year])
        if not lines:
            continue
        parts.append(str(year))
        parts.extend(lines)
        if i < len(sorted_years) - 1:
            parts.append("")
    return "\n".join(parts) + "\n"


def merge_archive(dest: str, label: str, archive_year: int, new_lines: list[str]) -> str:
    """合并：保留旧年份，更新/插入 archive_year。"""
    existing_label = label
    year_blocks: dict[int, list[str]] = {}

    if os.path.isfile(dest):
        with open(dest, encoding="utf-8") as f:
            old_label, year_blocks = parse_default_data(f.read())
        if old_label:
            existing_label = old_label

    if new_lines:
        year_blocks[archive_year] = list(new_lines)

    if not year_blocks:
        return f"{existing_label}\n\n"

    return build_multi_year_archive(existing_label, year_blocks)


def read_yuexun_lines(path: str) -> list[str]:
    """读取月循行（去掉空行、纯年份行）。"""
    with open(path, encoding="utf-8") as f:
        lines = []
        for raw in f:
            line = raw.strip()
            if not line or YEAR_RE.fullmatch(line):
                continue
            if YUEXUN_ISSUE_RE.search(line):
                lines.append(line)
        return lines


def parse_yuexun_years(content: str) -> dict[int, list[str]]:
    """解析 hkwlyxh 多年块：{年: [月循行]}。"""
    years: dict[int, list[str]] = {}
    current_year: int | None = None
    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            continue
        if YEAR_RE.fullmatch(line):
            current_year = int(line)
            years.setdefault(current_year, [])
            continue
        if current_year is not None and YUEXUN_ISSUE_RE.search(line):
            years[current_year].append(line)
    return years


def build_yuexun_archive(year_blocks: dict[int, list[str]]) -> str:
    """月循多年输出：新年份在上，期内倒序（与现有 hkwlyxh 一致）。"""
    parts: list[str] = []
    sorted_years = sorted(year_blocks.keys(), reverse=True)
    for i, year in enumerate(sorted_years):
        lines = sort_issue_lines(year_blocks[year], reverse=True)
        if not lines:
            continue
        parts.append(str(year))
        parts.extend(lines)
        if i < len(sorted_years) - 1:
            parts.append("")
    return ("\n".join(parts) + "\n") if parts else ""


def resolve_yuexun_dest() -> str:
    """优先 hkwlyxh.txt；若仅有旧名 wlhkyxh.txt 则沿用并写回新名。"""
    if os.path.isfile(YUEXUN_DEST):
        return YUEXUN_DEST
    if os.path.isfile(YUEXUN_DEST_LEGACY):
        return YUEXUN_DEST_LEGACY
    return YUEXUN_DEST


def archive_yuexun(archive_year: int) -> bool:
    """
    将 hkyxh.txt 整年内容写入 hkwlyxh.txt 的 archive_year 块。
    返回是否写文件有变更。
    """
    if not os.path.isfile(YUEXUN_SRC):
        print(f"跳过月循：未找到 {YUEXUN_SRC}")
        return False

    new_lines = read_yuexun_lines(YUEXUN_SRC)
    if not new_lines:
        print(f"跳过月循：{YUEXUN_SRC} 无有效期数行")
        return False

    dest_read = resolve_yuexun_dest()
    year_blocks: dict[int, list[str]] = {}
    old = ""
    if os.path.isfile(dest_read):
        with open(dest_read, encoding="utf-8") as f:
            old = f.read()
        year_blocks = parse_yuexun_years(old)

    year_blocks[archive_year] = list(new_lines)
    content = build_yuexun_archive(year_blocks)

    if old == content and dest_read == YUEXUN_DEST:
        print(f"未变化 {YUEXUN_DEST}（月循 {archive_year}，来源 {YUEXUN_SRC}）")
        return False

    with open(YUEXUN_DEST, "w", encoding="utf-8") as f:
        f.write(content)

    # 旧名存在且与新名不同时删除，避免双份
    if dest_read == YUEXUN_DEST_LEGACY and os.path.isfile(YUEXUN_DEST_LEGACY):
        try:
            os.remove(YUEXUN_DEST_LEGACY)
            print(f"已移除旧文件名 {YUEXUN_DEST_LEGACY}")
        except OSError as e:
            print(f"警告：无法删除 {YUEXUN_DEST_LEGACY}: {e}")

    years_info = ", ".join(
        f"{y}({len(year_blocks[y])}期)" for y in sorted(year_blocks.keys(), reverse=True)
    )
    print(f"已归档 {YUEXUN_SRC} → {YUEXUN_DEST}（月循，写入 {archive_year}，保留年份: {years_info}）")
    return True


def main() -> int:
    now = datetime.now(BJ)
    archive_year = now.year - 1
    force = "--force" in sys.argv

    if now.month != 1 or now.day != 1:
        print(f"当前北京时间 {now:%Y-%m-%d %H:%M:%S}，非 1 月 1 日；归档年份应为 {archive_year}")
        if not force:
            print("已跳过写入（避免误把当年数据归档）。元旦自动跑，或手动加 --force")
            return 0
        print("已指定 --force，继续写入")

    os.makedirs("defaultData", exist_ok=True)
    changed = 0

    for item in ARCHIVES:
        src = resolve_src(item["src"])
        dest = item["dest"]
        label = item["label"]

        if not src:
            print(f"跳过 {label}：未找到源文件 {item['src']}")
            continue

        lines = read_issue_lines(src)
        if not lines:
            print(f"跳过 {label}：{src} 无有效期数行")
            continue

        old = ""
        if os.path.isfile(dest):
            with open(dest, encoding="utf-8") as f:
                old = f.read()

        content = merge_archive(dest, label, archive_year, lines)

        if old == content:
            print(f"未变化 {dest}（{label} {archive_year}，来源 {src}）")
            continue

        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)
        changed += 1
        _, kept = parse_default_data(content)
        years_info = ", ".join(f"{y}({len(kept[y])}期)" for y in sorted(kept.keys(), reverse=True))
        print(f"已归档 {src} → {dest}（{label}，写入 {archive_year}，保留年份: {years_info}）")

    if archive_yuexun(archive_year):
        changed += 1

    if changed == 0:
        print("归档无变更（defaultData / hkwlyxh）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
