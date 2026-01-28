#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高频抓取 www.cjcp.cn 最新一期开奖数据，合并写入 lottery/。
对应 ssqiu.js / sand.js / kuaileba.js 的抓取解析逻辑。
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
LOTTERY_DIR = BASE_DIR / "lottery"

URLS = {
    "ssq": "https://www.cjcp.cn/kaijiang/ssq/",
    "3d": "https://www.cjcp.cn/kaijiang/3d/",
    "kl8": "https://www.cjcp.cn/kaijiang/fckl8/",
}

# 对应 lottery 下的 .js 文件及变量名
LOTTERY_FILES = {
    "ssq": ("ssqdefaultData.js", "ssqdefaultData", "// 双色球开奖数据\n"),
    "3d": ("sddefaultData.js", "sddefaultData", "// 3D开奖数据\n"),
    "kl8": ("defaultData.js", "defaultData", "// 快乐8开奖数据\n"),
}


def fetch_html(url: str, timeout: int = 20) -> str | None:
    for attempt in range(3):
        try:
            r = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                },
                timeout=timeout,
            )
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"  fetch {url} attempt {attempt + 1}/3: {e}")
            if attempt < 2:
                time.sleep(2)
    return None


def _year_period_from_text(text: str) -> tuple[str | None, str | None]:
    text = re.sub(r"\s+", " ", text)
    m = re.search(r"(20\d{2})(\d{3})", text)
    if m:
        return m.group(1), m.group(2)
    m = re.search(r"第\s*(\d{1,4})\s*期", text)
    period = m.group(1) if m else None
    m = re.search(r"(20\d{2})", text)
    year = m.group(1) if m else str(datetime.now().year)
    return year, period


def parse_latest_ssq(html: str) -> dict | None:
    """解析双色球最新一期，与 ssqiu.js parseLatestSSQFromHtml 逻辑一致。"""
    soup = BeautifulSoup(html, "html.parser")
    # 优先 div.kb_num.kj_num.public_num
    latest = soup.select_one("div.kb_num.kj_num.public_num")
    if not latest:
        latest = soup.select_one("div.kb_num.kj_num")
    if not latest:
        return None

    text = latest.get_text(" ", strip=True)
    year, period = _year_period_from_text(text)
    if not year or not period:
        return None

    period = period.zfill(3)
    if period == "000":
        return None

    reds = [int(s.get_text(strip=True)) for s in latest.select("span.qiu_red") if s.get_text(strip=True).isdigit()]
    blue_el = latest.select_one("span.qiu_blue")
    blue = int(blue_el.get_text(strip=True)) if blue_el and blue_el.get_text(strip=True).isdigit() else None

    if len(reds) != 6 or blue is None or not (1 <= blue <= 16):
        return None
    for r in reds:
        if not (1 <= r <= 33):
            return None

    reds.sort()
    numbers = reds + [blue]
    return {"year": year, "period": period, "numbers": numbers}


def parse_latest_3d(html: str) -> dict | None:
    """解析3D最新一期，与 sand.js parseLatest3DFromHtml 逻辑一致。"""
    soup = BeautifulSoup(html, "html.parser")
    latest = soup.select_one("div.kb_num.kj_num.public_num") or soup.select_one("div.kb_num.kj_num")
    if not latest:
        return None

    text = latest.get_text(" ", strip=True)
    year, period = _year_period_from_text(text)
    if not year or not period:
        return None

    period = period.zfill(3)
    if period == "000":
        return None

    nums = []
    for s in latest.select("span.qiu_red, span[class*='red'], span[class*='ball'], [class*='qiu']"):
        t = (s.get_text(strip=True) or "").strip()
        if re.match(r"^\d$", t):
            nums.append(int(t))
            if len(nums) >= 3:
                break
    if len(nums) != 3 or any(n < 0 or n > 9 for n in nums):
        return None

    return {"year": year, "period": period, "numbers": nums}


def parse_latest_kl8(html: str) -> dict | None:
    """解析快乐8最新一期，与 kuaileba.js parseLatestFromHtml 逻辑一致。"""
    soup = BeautifulSoup(html, "html.parser")
    latest = soup.select_one("div.kb_num.kj_num.public_num") or soup.select_one("div.kb_num.kj_num")
    if not latest:
        return None

    text = latest.get_text(" ", strip=True)
    year, period = _year_period_from_text(text)
    if not year or not period:
        return None

    period = period.zfill(3)
    if period == "000":
        return None

    nums = []
    for s in latest.select("span.qiu_red"):
        t = (s.get_text(strip=True) or "").strip()
        if t in ("-", "—", "－", "−") or not t or re.match(r"^[\s\-—－−]+$", t):
            break
        try:
            n = int(t)
            if 1 <= n <= 80 and n not in nums:
                nums.append(n)
                if len(nums) >= 20:
                    break
        except ValueError:
            continue
    if len(nums) != 20:
        return None

    nums.sort()
    return {"year": year, "period": period, "numbers": nums}


PARSERS = {
    "ssq": parse_latest_ssq,
    "3d": parse_latest_3d,
    "kl8": parse_latest_kl8,
}


def load_lottery_js(path: Path) -> dict:
    """从 lottery/*.js 解析出 { "2026": [ { period, numbers }, ... ] }。"""
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    idx = raw.find("=")
    if idx < 0:
        return {}
    idx = raw.find("{", idx)
    if idx < 0:
        return {}
    start = idx
    depth = 0
    for i, c in enumerate(raw[idx:], start=idx):
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                inner = raw[start : i + 1]
                break
    else:
        return {}
    inner = re.sub(r"\bperiod\s*:", '"period":', inner)
    inner = re.sub(r"\bnumbers\s*:", '"numbers":', inner)
    try:
        return json.loads(inner)
    except json.JSONDecodeError:
        return {}


def save_lottery_js(path: Path, data: dict, var_name: str, comment: str) -> None:
    """写回 lottery/*.js 格式。"""
    lines = [comment, f"const {var_name} = {{\n"]
    years = sorted(data.keys(), key=int)
    for yi, year in enumerate(years):
        arr = data[year]
        lines.append(f'  "{year}": [\n')
        for i, r in enumerate(arr):
            period = r["period"]
            nums = r["numbers"]
            nums_str = ", ".join(str(n) for n in nums)
            sep = "," if i < len(arr) - 1 else ""
            lines.append(f'    {{ period: "{period}", numbers: [{nums_str}] }}{sep}\n')
        lines.append("  ]" + ("," if yi < len(years) - 1 else "") + "\n")
    lines.append("};\n")
    path.write_text("".join(lines), encoding="utf-8")


def merge_record(annual: dict, record: dict) -> bool:
    """合并一条新记录，按期号去重。返回是否有新增。"""
    year = record["year"]
    period = record["period"]
    if year not in annual:
        annual[year] = []
    for r in annual[year]:
        if r["period"] == period:
            return False
    annual[year].append({"period": period, "numbers": list(record["numbers"])})
    annual[year].sort(key=lambda x: int(x["period"]))
    return True


def main() -> int:
    lottery_dir = Path(LOTTERY_DIR)
    lottery_dir.mkdir(parents=True, exist_ok=True)
    updated = []

    for key, (filename, var_name, comment) in LOTTERY_FILES.items():
        url = URLS[key]
        parse_fn = PARSERS[key]
        path = lottery_dir / filename

        print(f"[{key}] fetch {url}")
        html = fetch_html(url)
        if not html or len(html) < 500:
            print(f"  skip {key}: no html")
            continue

        rec = parse_fn(html)
        if not rec:
            print(f"  skip {key}: parse latest failed")
            continue
        print(f"  latest: {rec['year']} {rec['period']}")

        data = load_lottery_js(path)
        if merge_record(data, rec):
            save_lottery_js(path, data, var_name, comment)
            updated.append(f"lottery/{filename}")
            print(f"  merged -> {path}")
        else:
            print(f"  no new record")

    if updated:
        print("Updated:", ", ".join(updated))
    else:
        print("No files updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
