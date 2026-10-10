#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每年 1 月 1–3 日（北京时间）可归档（元旦主跑 + 漏跑补档）：

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

2) 港彩月循：hkyxh.txt → hkwlyxh.txt（按年份，期内倒序）
     2026
     08.11 → 087期: 13馬 → 猴鸡
     ...
     2025
     12.28 → 134期: 45雞 → 马羊

3) 港彩日冲：hkrc.txt → hkwlrc.txt（按年份，期内正序，与现有 hkwlrc 一致）
     2026
     001期：22猴 → 羊日冲牛
     ...
     2025
     001期：...
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
# 北京时间 1 月 1–3 日可写（1 日主跑，2–3 日补档）；其它日期需 --force
ARCHIVE_WINDOW_DAYS = (1, 2, 3)

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

# 当年日冲 → 往年日冲（按年）
RICHONG_SRC = "hkrc.txt"
RICHONG_DEST = "hkwlrc.txt"


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


def read_period_lines(path: str) -> list[str]:
    """读取含「N期」的行（月循/日冲；去掉空行、纯年份行）。"""
    with open(path, encoding="utf-8") as f:
        lines = []
        for raw in f:
            line = raw.strip()
            if not line or YEAR_RE.fullmatch(line):
                continue
            if YUEXUN_ISSUE_RE.search(line):
                lines.append(line)
        return lines


def parse_period_years(content: str) -> dict[int, list[str]]:
    """解析按年分块的月循/日冲文件：{年: [行]}。"""
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


def build_period_archive(year_blocks: dict[int, list[str]], *, reverse_within_year: bool) -> str:
    """多年输出：新年份在上；期内顺序由 reverse_within_year 控制。"""
    parts: list[str] = []
    sorted_years = sorted(year_blocks.keys(), reverse=True)
    for i, year in enumerate(sorted_years):
        lines = sort_issue_lines(year_blocks[year], reverse=reverse_within_year)
        if not lines:
            continue
        parts.append(str(year))
        parts.extend(lines)
        if i < len(sorted_years) - 1:
            parts.append("")
    return ("\n".join(parts) + "\n") if parts else ""


def merge_period_lines(old_lines: list[str], new_lines: list[str]) -> list[str]:
    """按期号合并：同源期号以新行为准，保留归档里已有、源里已消失的期（防元旦后源被清空）。"""
    by_issue: dict[int, str] = {}
    for line in old_lines:
        m = YUEXUN_ISSUE_RE.search(line)
        if m:
            by_issue[int(m.group(1))] = line
    for line in new_lines:
        m = YUEXUN_ISSUE_RE.search(line)
        if m:
            by_issue[int(m.group(1))] = line
    return list(by_issue.values())


def resolve_yuexun_dest() -> str:
    """优先 hkwlyxh.txt；若仅有旧名 wlhkyxh.txt 则沿用并写回新名。"""
    if os.path.isfile(YUEXUN_DEST):
        return YUEXUN_DEST
    if os.path.isfile(YUEXUN_DEST_LEGACY):
        return YUEXUN_DEST_LEGACY
    return YUEXUN_DEST


def archive_period_file(
    *,
    src: str,
    dest: str,
    archive_year: int,
    kind: str,
    reverse_within_year: bool,
    dest_read: str | None = None,
    dest_write: str | None = None,
    legacy_cleanup: str | None = None,
) -> bool:
    """
    将当年源文件写入按年归档目标的 archive_year 块。
    返回是否写文件有变更。
    """
    dest_read = dest_read or dest
    dest_write = dest_write or dest

    if not os.path.isfile(src):
        print(f"跳过{kind}：未找到 {src}")
        return False

    new_lines = read_period_lines(src)
    if not new_lines:
        print(f"跳过{kind}：{src} 无有效期数行")
        return False

    year_blocks: dict[int, list[str]] = {}
    old = ""
    if os.path.isfile(dest_read):
        with open(dest_read, encoding="utf-8") as f:
            old = f.read()
        year_blocks = parse_period_years(old)

    merged = merge_period_lines(year_blocks.get(archive_year, []), new_lines)
    year_blocks[archive_year] = merged
    content = build_period_archive(year_blocks, reverse_within_year=reverse_within_year)

    if old == content and dest_read == dest_write:
        print(f"未变化 {dest_write}（{kind} {archive_year}，来源 {src}）")
        return False

    with open(dest_write, "w", encoding="utf-8") as f:
        f.write(content)

    if legacy_cleanup and legacy_cleanup != dest_write and os.path.isfile(legacy_cleanup):
        try:
            os.remove(legacy_cleanup)
            print(f"已移除旧文件名 {legacy_cleanup}")
        except OSError as e:
            print(f"警告：无法删除 {legacy_cleanup}: {e}")

    years_info = ", ".join(
        f"{y}({len(year_blocks[y])}期)" for y in sorted(year_blocks.keys(), reverse=True)
    )
    print(f"已归档 {src} → {dest_write}（{kind}，写入 {archive_year}，保留年份: {years_info}）")
    return True


def archive_yuexun(archive_year: int) -> bool:
    """将 hkyxh.txt 整年内容写入 hkwlyxh.txt 的 archive_year 块（期内倒序）。"""
    dest_read = resolve_yuexun_dest()
    return archive_period_file(
        src=YUEXUN_SRC,
        dest=YUEXUN_DEST,
        archive_year=archive_year,
        kind="月循",
        reverse_within_year=True,
        dest_read=dest_read,
        dest_write=YUEXUN_DEST,
        legacy_cleanup=YUEXUN_DEST_LEGACY if dest_read == YUEXUN_DEST_LEGACY else None,
    )


def archive_richong(archive_year: int) -> bool:
    """将 hkrc.txt 整年内容写入 hkwlrc.txt 的 archive_year 块（期内正序）。"""
    return archive_period_file(
        src=RICHONG_SRC,
        dest=RICHONG_DEST,
        archive_year=archive_year,
        kind="日冲",
        reverse_within_year=False,
    )


def default_data_year_count(dest: str, year: int) -> int:
    if not os.path.isfile(dest):
        return 0
    with open(dest, encoding="utf-8") as f:
        _, years = parse_default_data(f.read())
    return len(years.get(year, []))


def period_file_year_count(dest: str, year: int) -> int:
    if not os.path.isfile(dest):
        return 0
    with open(dest, encoding="utf-8") as f:
        years = parse_period_years(f.read())
    return len(years.get(year, []))


def is_year_adequately_archived(archive_year: int, *, min_ratio: float = 0.8) -> bool:
    """
    判断 archive_year 是否已充分写入各归档目标。
    仅校验「源文件仍明显持有上一年数据」(期数 > 1) 的项；
    源已滚到仅 001/空 时跳过该项（无法再从源补档）。
    """
    pending: list[str] = []

    for item in ARCHIVES:
        src = resolve_src(item["src"])
        if not src:
            continue
        src_n = len(read_issue_lines(src))
        if src_n <= 1:
            continue
        dest_n = default_data_year_count(item["dest"], archive_year)
        need = max(1, int(src_n * min_ratio))
        if dest_n < need:
            pending.append(f"{item['label']} {dest_n}/{src_n}")

    if os.path.isfile(YUEXUN_SRC):
        src_n = len(read_period_lines(YUEXUN_SRC))
        if src_n > 1:
            dest = resolve_yuexun_dest()
            dest_n = period_file_year_count(dest, archive_year)
            need = max(1, int(src_n * min_ratio))
            if dest_n < need:
                pending.append(f"月循 {dest_n}/{src_n}")

    if os.path.isfile(RICHONG_SRC):
        src_n = len(read_period_lines(RICHONG_SRC))
        if src_n > 1:
            dest_n = period_file_year_count(RICHONG_DEST, archive_year)
            need = max(1, int(src_n * min_ratio))
            if dest_n < need:
                pending.append(f"日冲 {dest_n}/{src_n}")

    if pending:
        print(f"归档未就绪 {archive_year}：{', '.join(pending)}")
        return False
    return True


def run_archive(archive_year: int, *, force: bool = False) -> int:
    """执行归档写入。返回有变更的文件数。force 时忽略 1/1–1/3 日期窗口。"""
    now = datetime.now(BJ)
    in_window = now.month == 1 and now.day in ARCHIVE_WINDOW_DAYS

    if not in_window and not force:
        print(
            f"当前北京时间 {now:%Y-%m-%d %H:%M:%S}，不在 1 月 {ARCHIVE_WINDOW_DAYS[0]}–"
            f"{ARCHIVE_WINDOW_DAYS[-1]} 日窗口；归档年份应为 {archive_year}"
        )
        print("已跳过写入（避免误把当年数据归档）。元旦/补档自动跑，或手动加 --force")
        return 0

    if force and not in_window:
        print(f"强制归档 {archive_year}（当前北京时间 {now:%Y-%m-%d %H:%M:%S}）")
    elif in_window and now.day != 1:
        print(f"当前北京时间 {now:%Y-%m-%d %H:%M:%S}，补档窗口日；归档年份 {archive_year}")

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
    if archive_richong(archive_year):
        changed += 1

    if changed == 0:
        print("归档无变更（defaultData / hkwlyxh / hkwlrc）")
    return changed


def ensure_archived_for_rollover(archive_year: int | None = None) -> bool:
    """
    新年 001 清空源文件前调用：若上一年尚未充分归档则强制补档。
    返回 True 表示可以安全清空；False 表示仍未就绪，调用方应暂不清空。
    """
    if archive_year is None:
        archive_year = datetime.now(BJ).year - 1

    if is_year_adequately_archived(archive_year):
        print(f"上一年 {archive_year} 已归档，允许清空并写入 001")
        return True

    print(f"上一年 {archive_year} 未归档或覆盖不足，001 清空前强制补档…")
    run_archive(archive_year, force=True)

    ok = is_year_adequately_archived(archive_year)
    if ok:
        print(f"补档成功：{archive_year} 已就绪，允许清空")
    else:
        print(f"补档后仍未就绪：{archive_year}，禁止清空源文件")
    return ok


def main() -> int:
    now = datetime.now(BJ)
    archive_year = now.year - 1
    force = "--force" in sys.argv
    run_archive(archive_year, force=force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
