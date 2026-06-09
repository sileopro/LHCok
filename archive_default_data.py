#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每年 1 月 1 日（北京时间）将根目录开奖 txt 归档到 defaultData/。

根目录文件名（zuikuai.py 实际写入）→ defaultData 对应文件：
  hk.txt   → defaultData/hk.txt   港彩 hk
  xam.txt  → defaultData/nz.txt   新澳 nz
  lam.txt  → defaultData/au.txt   老澳 au
  klb.txt  → defaultData/tw.txt   台彩 tw（若无则尝试 tc.txt）
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

BJ = ZoneInfo("Asia/Shanghai")
ISSUE_RE = re.compile(r"第(\d{1,3})期")

ARCHIVES = [
    {"src": ["hk.txt"], "dest": "defaultData/hk.txt", "label": "港彩 hk"},
    {"src": ["xam.txt"], "dest": "defaultData/nz.txt", "label": "新澳 nz"},
    {"src": ["lam.txt"], "dest": "defaultData/au.txt", "label": "老澳 au"},
    {"src": ["klb.txt", "tc.txt"], "dest": "defaultData/tw.txt", "label": "台彩 tw"},
]


def resolve_src(paths: list[str]) -> str | None:
    for name in paths:
        if os.path.isfile(name):
            return name
    return None


def read_issue_lines(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        lines = []
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("港彩") or line.startswith("新澳") or line.startswith("老澳") or line.startswith("台彩"):
                continue
            if re.fullmatch(r"\d{4}", line):
                continue
            lines.append(line)
        return lines


def sort_issue_lines(lines: list[str]) -> list[str]:
    def issue_num(line: str) -> int:
        m = ISSUE_RE.search(line)
        return int(m.group(1)) if m else 0

    return sorted(lines, key=issue_num)


def build_archive(label: str, year: int, lines: list[str]) -> str:
    body = "\n".join(sort_issue_lines(lines))
    if body:
        return f"{label}\n{year}\n{body}\n"
    return f"{label}\n{year}\n\n"


def main() -> int:
    now = datetime.now(BJ)
    archive_year = now.year - 1

    if now.month != 1 or now.day != 1:
        print(f"当前北京时间 {now:%Y-%m-%d %H:%M:%S}，非 1 月 1 日；仍将归档年份设为 {archive_year}")

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

        content = build_archive(label, archive_year, lines)
        old = ""
        if os.path.isfile(dest):
            with open(dest, encoding="utf-8") as f:
                old = f.read()

        if old == content:
            print(f"未变化 {dest}（{label} {archive_year}，来源 {src}）")
            continue

        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)
        changed += 1
        print(f"已归档 {src} → {dest}（{label} {archive_year}，共 {len(lines)} 期）")

    if changed == 0:
        print("defaultData 无变更")
    return 0


if __name__ == "__main__":
    sys.exit(main())
