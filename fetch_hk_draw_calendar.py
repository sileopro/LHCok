#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从香港马会官网 Sitecore 抓取六合彩搅珠日期 / 金多宝，写入 lottery.txt。

供 GitHub Actions 在每月 15、16 日运行（官网大约月中公布下月赛程）。
格式与 App 解析一致：
  2026.09: 1,3,5,8,10,12,15,17,19,22,26,29 金多宝26
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime

API_URL = "https://consvc.hkjc.com/JCBW/api/graph"
API_KEY = "{FF2309B7-E8BB-49B2-82A7-36AE0B48F171}"
SITECORE_PATH = "/sitecore/content/Sites/JCBW/NextDrawSchedule/Schedule"
QUERY = (
    "query MarksixFixtures($path: String!, $lang: String!) { "
    "legends: item(path: \"/sitecore/content/Sites/JCBW/NextDrawSchedule/DrawTypeLegend\", language: $lang) { "
    "children { key: name name: field(name: \"LegendName\") { value } } } "
    "item(path: $path, language: $lang) { years: children { year: name months: children { "
    "key: name month: field(name: \"DrawMonth\") { value } "
    "dates: field(name: \"NormalDrawDates\") { ... on MultilistField { date: targetItems { value: name } } } "
    "snowballs: field(name: \"SnowballDrawDates\") { ... on MultilistField { date: targetItems { value: name } } } "
    "} } } }"
)
LINE_RE = re.compile(r"^(\d{4})[.\-/](\d{1,2})\s*[:：]\s*(.+)$")
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(ROOT, "lottery.txt")


def fetch_official() -> dict:
    payload = json.dumps(
        {
            "operationName": "MarksixFixtures",
            "variables": {"path": SITECORE_PATH, "lang": "zh-HK"},
            "query": QUERY,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(API_URL, data=payload, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("Accept", "application/json")
    req.add_header("sc_apikey", API_KEY)
    req.add_header("Origin", "https://bet.hkjc.com")
    req.add_header("Referer", "https://bet.hkjc.com/ch/marksix/fixtures")
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (compatible; LHCok-calendar-bot/1.0; +https://github.com/sileopro/LHCok)",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError("官网 HTTP %s: %s" % (e.code, body[:400])) from e
    except urllib.error.URLError as e:
        raise RuntimeError("官网连接失败: %s" % e.reason) from e
    data = json.loads(raw)
    if not isinstance(data, dict) or not data.get("data"):
        raise RuntimeError("官网返回无效 JSON")
    return data


def _days_from_field(field) -> list:
    out = []
    if not field or not isinstance(field, dict):
        return out
    items = field.get("date") or []
    if not isinstance(items, list):
        return out
    for item in items:
        try:
            n = int(str((item or {}).get("value") or "").strip())
        except (TypeError, ValueError):
            continue
        if 1 <= n <= 31 and n not in out:
            out.append(n)
    out.sort()
    return out


def parse_official(data: dict) -> dict:
    years = (((data.get("data") or {}).get("item") or {}).get("years")) or []
    months = {}
    for y in years:
        year = str((y or {}).get("year") or "").strip()
        if not re.match(r"^\d{4}$", year):
            continue
        for mo in (y or {}).get("months") or []:
            month_raw = ((mo or {}).get("month") or {}).get("value") or (mo or {}).get("key")
            try:
                month = int(str(month_raw).strip())
            except (TypeError, ValueError):
                continue
            if month < 1 or month > 12:
                continue
            key = "%s.%02d" % (year, month)
            draws = _days_from_field((mo or {}).get("dates"))
            jackpots = _days_from_field((mo or {}).get("snowballs"))
            for n in jackpots:
                if n not in draws:
                    draws.append(n)
            draws.sort()
            if draws or jackpots:
                months[key] = {"draw": draws, "jackpot": jackpots}
    return months


def parse_existing(text: str) -> dict:
    months = {}
    if not text:
        return months
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = LINE_RE.match(line)
        if not m:
            continue
        year, month, rest = m.group(1), int(m.group(2)), m.group(3)
        key = "%s.%02d" % (year, month)
        jackpots = []
        draw_part = rest
        jidx = rest.find("金多宝")
        if jidx >= 0:
            draw_part = rest[:jidx].strip()
            jackpots = _parse_day_list(rest[jidx + 3 :])
        draws = _parse_day_list(draw_part)
        if draws or jackpots:
            months[key] = {"draw": draws, "jackpot": jackpots}
    return months


def _parse_day_list(s: str) -> list:
    out = []
    for part in re.split(r"[,，、\s]+", str(s or "")):
        part = part.strip()
        if not part:
            continue
        try:
            n = int(part)
        except ValueError:
            continue
        if 1 <= n <= 31 and n not in out:
            out.append(n)
    out.sort()
    return out


def format_file(months: dict) -> str:
    """保持原格式：2026.09: 1,3,5,8,10,12,15,17,19,22,26,29 金多宝26"""
    keys = sorted(months.keys(), reverse=True)
    lines = []
    for key in keys:
        item = months[key]
        draws = ",".join(str(d) for d in item.get("draw") or [])
        line = "%s: %s" % (key, draws)
        jackpots = item.get("jackpot") or []
        if jackpots:
            line += " 金多宝%s" % ",".join(str(d) for d in jackpots)
        lines.append(line.rstrip())
    return "\n".join(lines) + "\n"


def next_month_key(now=None) -> str:
    now = now or datetime.now()
    if now.month == 12:
        return "%d.01" % (now.year + 1)
    return "%d.%02d" % (now.year, now.month + 1)


def main() -> int:
    print("从马会官网抓取搅珠日期...")
    try:
        official = parse_official(fetch_official())
    except Exception as e:
        print("本次抓取失败（后续定时会再试）: %s" % e, file=sys.stderr)
        return 1
    if not official:
        print("官网未返回任何月份，放弃写入；后续定时会再试", file=sys.stderr)
        return 1
    existing = {}
    if os.path.isfile(OUT_PATH):
        with open(OUT_PATH, "r", encoding="utf-8") as f:
            existing = parse_existing(f.read())
    merged = dict(existing)
    merged.update(official)
    text = format_file(merged)
    old = ""
    if os.path.isfile(OUT_PATH):
        with open(OUT_PATH, "r", encoding="utf-8") as f:
            old = f.read()
    nxt = next_month_key()
    has_next = nxt in official or nxt in merged
    if old.replace("\r\n", "\n") == text:
        print("lottery.txt 无变化（官网 %d 个月份）" % len(official))
        if datetime.now().day >= 15 and not has_next:
            print("官网尚未公布 %s，15–28 日会继续定时抓取" % nxt)
        return 0
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("已写入 lottery.txt，官网月份 %d，合并后 %d" % (len(official), len(merged)))
    print("---")
    print(text)
    print("抓取时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if datetime.now().day >= 15 and not has_next:
        print("官网尚未公布 %s，15–28 日会继续定时抓取" % nxt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
