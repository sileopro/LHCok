#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高频抓取 500.com 最新一期开奖数据，合并写入 lottery/。
参考 grab500_ssq.py 的解析逻辑。
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
    "ssq": "http://zx.500.com/ssq/",
    "3d": "https://zx.500.com/sd/",
    "kl8": "https://kaijiang.500.com/kl8.shtml",
}

# 对应 lottery 下的 .js 文件及变量名
LOTTERY_FILES = {
    "ssq": ("ssqdefaultData.js", "ssqdefaultData", "// 双色球开奖数据\n"),
    "3d": ("sddefaultData.js", "sddefaultData", "// 3D开奖数据\n"),
    "kl8": ("defaultData.js", "defaultData", "// 快乐8开奖数据\n"),
}


def fetch_html(url: str, timeout: int = 20) -> str | None:
    """获取网页内容，参考 grab500_ssq.py 的简单方式。"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    
    for attempt in range(3):
        try:
            r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"  fetch {url} attempt {attempt + 1}/3: {e}")
            if attempt < 2:
                time.sleep(1)
    return None


# _year_period_from_text 函数已不再需要，保留以防 kl8 使用
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
    """解析双色球最新一期，参考 grab500_ssq.py 的正则表达式方式。"""
    # 期号：<dt>([0-9]\d*).*</dt>
    period_match = re.search(r'<dt>([0-9]\d*).*?</dt>', html)
    if not period_match:
        return None
    
    period_full = period_match.group(1)
    # 期号可能是 7 位（如 2026001）或 3 位（如 001）
    if len(period_full) >= 7:
        year = period_full[:4]
        period = period_full[4:]
    elif len(period_full) >= 3:
        year = str(datetime.now().year)
        period = period_full[-3:]
    else:
        year = str(datetime.now().year)
        period = period_full.zfill(3)
    
    period = period.zfill(3)
    
    # 红球：<li class="redball">([0-9]\d*)</li>
    red_matches = re.findall(r'<li class="redball">([0-9]\d*)</li>', html)
    reds = [int(r) for r in red_matches if r.isdigit() and 1 <= int(r) <= 33]
    
    # 蓝球：<li class="blueball">([0-9]\d*)</li>
    blue_match = re.search(r'<li class="blueball">([0-9]\d*)</li>', html)
    blue = int(blue_match.group(1)) if blue_match and blue_match.group(1).isdigit() else None
    
    if len(reds) != 6 or blue is None or not (1 <= blue <= 16):
        return None
    
    reds.sort()
    numbers = reds + [blue]
    return {"year": year, "period": period, "numbers": numbers}


def parse_latest_3d(html: str) -> dict | None:
    """解析3D最新一期，参考 500.com 的 HTML 结构。"""
    # 尝试使用类似双色球的解析方式
    # 期号：<dt>([0-9]\d*).*</dt>
    period_match = re.search(r'<dt>([0-9]\d*).*?</dt>', html)
    if not period_match:
        return None
    
    period_full = period_match.group(1)
    if len(period_full) >= 7:
        year = period_full[:4]
        period = period_full[4:]
    elif len(period_full) >= 3:
        year = str(datetime.now().year)
        period = period_full[-3:]
    else:
        year = str(datetime.now().year)
        period = period_full.zfill(3)
    
    period = period.zfill(3)
    
    # 3D 号码：可能是 <li class="ball"> 或类似结构
    # 尝试多种可能的选择器
    nums = []
    
    # 方式1：查找 <li class="ball"> 或 <li class="redball">
    ball_matches = re.findall(r'<li class="(?:ball|redball)">([0-9])</li>', html)
    if ball_matches:
        nums = [int(b) for b in ball_matches if b.isdigit() and 0 <= int(b) <= 9]
    
    # 方式2：如果方式1失败，尝试 BeautifulSoup
    if len(nums) != 3:
        soup = BeautifulSoup(html, "html.parser")
        balls = soup.select('li.ball, li.redball, li[class*="ball"]')
        nums = []
        for ball in balls:
            text = ball.get_text(strip=True)
            if re.match(r"^\d$", text):
                n = int(text)
                if 0 <= n <= 9:
                    nums.append(n)
                    if len(nums) >= 3:
                        break
    
    if len(nums) != 3 or any(n < 0 or n > 9 for n in nums):
        return None
    
    return {"year": year, "period": period, "numbers": nums}


def parse_latest_kl8(html: str) -> dict | None:
    """解析快乐8最新一期，参考 500.com 的 HTML 结构。"""
    # 查找期号：可能是链接中的 2025212 格式，或页面中的期号文本
    period_match = re.search(r'快乐8\s*[第]?\s*(\d{7})', html)
    if not period_match:
        # 尝试从链接中提取：/shtml/kl8/2025212.shtml
        period_match = re.search(r'/shtml/kl8/(\d{7})', html)
    if not period_match:
        # 尝试查找页面中的期号显示
        period_match = re.search(r'(\d{4})(\d{3})\s*期', html)
        if period_match:
            year = period_match.group(1)
            period = period_match.group(2)
        else:
            return None
    else:
        period_full = period_match.group(1)
        if len(period_full) == 7:
            year = period_full[:4]
            period = period_full[4:]
        else:
            return None
    
    period = period.zfill(3)
    
    # 查找开奖号码：在页面中可能是 "开奖号码：" 后面的数字
    # 格式可能是：03 10 12 28 ... 或 <li>03</li> <li>10</li> ...
    nums = []
    
    # 方式1：查找 "开奖号码：" 后面的文本
    numbers_match = re.search(r'开奖号码[：:]\s*([\d\s\-—－−]+)', html)
    if numbers_match:
        numbers_text = numbers_match.group(1)
        # 提取所有数字
        number_matches = re.findall(r'\d+', numbers_text)
        for num_str in number_matches:
            try:
                n = int(num_str)
                if 1 <= n <= 80 and n not in nums:
                    nums.append(n)
                    if len(nums) >= 20:
                        break
            except ValueError:
                continue
    
    # 方式2：如果方式1失败，尝试 BeautifulSoup 查找号码球
    if len(nums) != 20:
        soup = BeautifulSoup(html, "html.parser")
        # 查找所有可能的号码元素
        balls = soup.select('li, span, td, div')
        nums = []
        for ball in balls:
            text = ball.get_text(strip=True)
            # 检查是否是 1-80 的数字
            if re.match(r'^\d{1,2}$', text):
                try:
                    n = int(text)
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
        if not html or len(html) < 200:
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
