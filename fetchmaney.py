#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高频抓取 500.com 最新一期开奖数据，合并写入 lottery/。

优先使用 m.500.com 移动开奖页（JS 变量 expect / opencode，抗反爬更稳），
失败再回退 kaijiang / zx 页面解析。
"""
from __future__ import annotations

import json
import re
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 自动检查和安装依赖
def check_and_install_dependencies():
    """检查并自动安装缺失的依赖包"""
    required_packages = {
        "requests": "requests>=2.28.0",
        "bs4": "beautifulsoup4>=4.11.0",
        "cloudscraper": "cloudscraper>=1.2.71",
    }

    missing_packages = []
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print(f"检测到缺失的依赖包: {', '.join(missing_packages)}")
        print("正在自动安装...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet", "--user"]
                + missing_packages
            )
            print("依赖安装完成！")
            import importlib

            importlib.invalidate_caches()
        except subprocess.CalledProcessError:
            print("自动安装失败，请手动运行: pip install -r requirements.txt")
            sys.exit(1)


check_and_install_dependencies()

import requests
from bs4 import BeautifulSoup

try:
    import cloudscraper

    _SESSION = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )
except Exception:
    _SESSION = requests.Session()

BASE_DIR = Path(__file__).resolve().parent
LOTTERY_DIR = BASE_DIR / "lottery"

# 每个彩种按优先级尝试多个 URL（移动站最稳）
URLS = {
    "ssq": [
        "https://m.500.com/info/kaijiang/ssq/",
        "https://kaijiang.500.com/ssq.shtml",
        "https://kaijiang.500.com/shtml/ssq/",
        "http://zx.500.com/ssq/",
    ],
    "3d": [
        "https://m.500.com/info/kaijiang/sd/",
        "https://kaijiang.500.com/sd.shtml",
        "https://zx.500.com/sd/",
    ],
    "kl8": [
        "https://m.500.com/info/kaijiang/kl8/",
        "https://kaijiang.500.com/kl8.shtml",
    ],
    "dlt": [
        "https://m.500.com/info/kaijiang/dlt/",
        "https://kaijiang.500.com/dlt.shtml",
        "https://www.cjcp.cn/kaijiang/dlt/",
        "https://zx.500.com/dlt/",
    ],
}

LOTTERY_FILES = {
    "ssq": ("ssqdefaultData.js", "ssqdefaultData", "// 双色球开奖数据\n"),
    "3d": ("sddefaultData.js", "sddefaultData", "// 3D开奖数据\n"),
    "kl8": ("defaultData.js", "defaultData", "// 快乐8开奖数据\n"),
    "dlt": ("dltdefaultData.js", "dltdefaultData", "// 大乐透开奖数据\n"),
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.500.com/",
}


def decode_response(resp: requests.Response) -> str:
    """500.com 多为 gbk/gb2312，优先按声明编码解码。"""
    raw = resp.content
    ctype = (resp.headers.get("Content-Type") or "").lower()
    candidates: list[str] = []
    if "gbk" in ctype or "gb2312" in ctype:
        candidates.extend(["gbk", "gb2312"])
    if resp.encoding and resp.encoding.lower() not in ("iso-8859-1", "ascii"):
        candidates.append(resp.encoding)
    candidates.extend(["gbk", "gb2312", "utf-8"])
    seen: set[str] = set()
    for enc in candidates:
        key = enc.lower()
        if key in seen:
            continue
        seen.add(key)
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="replace")


def is_bot_challenge(html: str) -> bool:
    return (
        "__tst_status" in html
        or "EO_Bot_Ssid" in html
        or ("function a(a)" in html and len(html) < 3000)
    )


def fetch_html(url: str, timeout: int = 20) -> str | None:
    for attempt in range(3):
        try:
            r = _SESSION.get(
                url, headers=HEADERS, timeout=timeout, allow_redirects=True
            )
            r.raise_for_status()
            text = decode_response(r)
            if is_bot_challenge(text):
                print(f"  fetch {url} attempt {attempt + 1}/3: bot challenge page")
                if attempt < 2:
                    time.sleep(1.5)
                continue
            if len(text) < 200:
                print(f"  fetch {url} attempt {attempt + 1}/3: too short ({len(text)})")
                if attempt < 2:
                    time.sleep(1)
                continue
            return text
        except Exception as e:
            print(f"  fetch {url} attempt {attempt + 1}/3: {e}")
            if attempt < 2:
                time.sleep(1)
    return None


def split_issue(issue: str) -> tuple[str, str] | None:
    """
    期号归一化：
    - 2026236 / 2026090 -> year=2026, period=236/090
    - 26102 / 26100     -> year=2026, period=102/100  (YY + PPP)
    - 2026001           -> year=2026, period=001
    """
    issue = issue.strip()
    if not issue.isdigit():
        return None
    if len(issue) >= 7 and issue.startswith("20"):
        return issue[:4], issue[4:].zfill(3)
    if len(issue) == 5:
        return "20" + issue[:2], issue[2:].zfill(3)
    if len(issue) == 6 and not issue.startswith("20"):
        # 极少见：YYNNNN
        return "20" + issue[:2], issue[2:].zfill(3)
    if len(issue) >= 3:
        return str(datetime.now().year), issue[-3:].zfill(3)
    return None


def parse_mobile_expect_opencode(html: str, kind: str) -> dict | None:
    """
    解析 m.500.com：
      expect  = '26102',
      opencode= '03,04,10,13,16,25|09',
    """
    m_exp = re.search(r"expect\s*=\s*'([^']+)'", html)
    m_code = re.search(r"opencode\s*=\s*'([^']+)'", html)
    if not m_exp or not m_code:
        return None

    yp = split_issue(m_exp.group(1))
    if not yp:
        return None
    year, period = yp

    raw = m_code.group(1).strip()
    if "|" in raw:
        front, back = raw.split("|", 1)
        nums = [int(x) for x in re.findall(r"\d+", front)]
        nums += [int(x) for x in re.findall(r"\d+", back)]
    else:
        nums = [int(x) for x in re.findall(r"\d+", raw)]

    if kind == "ssq":
        if len(nums) != 7:
            return None
        reds, blue = nums[:6], nums[6]
        if not all(1 <= n <= 33 for n in reds) or not (1 <= blue <= 16):
            return None
        reds = sorted(reds)
        return {"year": year, "period": period, "numbers": reds + [blue]}

    if kind == "dlt":
        if len(nums) != 7:
            return None
        if not all(1 <= nums[i] <= 35 for i in range(5)):
            return None
        if not all(1 <= nums[i] <= 12 for i in range(5, 7)):
            return None
        return {"year": year, "period": period, "numbers": nums}

    if kind == "3d":
        if len(nums) != 3 or any(n < 0 or n > 9 for n in nums):
            return None
        return {"year": year, "period": period, "numbers": nums}

    if kind == "kl8":
        if len(nums) != 20:
            return None
        if not all(1 <= n <= 80 for n in nums):
            return None
        return {"year": year, "period": period, "numbers": sorted(nums)}

    return None


def parse_latest_ssq(html: str) -> dict | None:
    rec = parse_mobile_expect_opencode(html, "ssq")
    if rec:
        return rec

    # kaijiang：ball_red / ball_blue
    period_match = re.search(
        r"(?:ssq/|第\s*)(\d{5,7})", html
    ) or re.search(r"<dt>([0-9]\d*).*?</dt>", html)
    if not period_match:
        return None
    yp = split_issue(period_match.group(1))
    if not yp:
        return None
    year, period = yp

    reds = [int(x) for x in re.findall(r'<li class="(?:ball_red|redball)">\s*0*(\d+)\s*</li>', html)]
    blues = [int(x) for x in re.findall(r'<li class="(?:ball_blue|blueball)">\s*0*(\d+)\s*</li>', html)]
    reds = [n for n in reds if 1 <= n <= 33][:6]
    blue = next((n for n in blues if 1 <= n <= 16), None)
    if len(reds) != 6 or blue is None:
        return None
    reds.sort()
    return {"year": year, "period": period, "numbers": reds + [blue]}


def parse_latest_3d(html: str) -> dict | None:
    rec = parse_mobile_expect_opencode(html, "3d")
    if rec:
        return rec

    period_match = re.search(
        r"(?:sd/|第\s*)(20\d{5}|\d{5,7})", html
    ) or re.search(r"<dt>([0-9]\d*).*?</dt>", html)
    if not period_match:
        return None
    yp = split_issue(period_match.group(1))
    if not yp:
        return None
    year, period = yp

    nums = [
        int(x)
        for x in re.findall(
            r'<li class="(?:ball_orange|ball|redball)">\s*(\d)\s*</li>', html
        )
    ]
    if len(nums) != 3:
        soup = BeautifulSoup(html, "html.parser")
        nums = []
        for ball in soup.select("li.ball_orange, li.ball, li.redball, li[class*='ball']"):
            text = ball.get_text(strip=True)
            if re.match(r"^\d$", text):
                nums.append(int(text))
                if len(nums) >= 3:
                    break
    if len(nums) != 3 or any(n < 0 or n > 9 for n in nums):
        return None
    return {"year": year, "period": period, "numbers": nums}


def parse_latest_dlt(html: str) -> dict | None:
    rec = parse_mobile_expect_opencode(html, "dlt")
    if rec:
        return rec

    # zx.500.com：kj_expect + redball / blueball
    m_opt = re.search(r'<option value="(\d{5,})"\s+selected="selected"', html)
    reds_500 = re.findall(r'<li class="(?:ball_red|redball)">\s*0*(\d+)\s*</li>', html)
    blues_500 = re.findall(r'<li class="(?:ball_blue|blueball)">\s*0*(\d+)\s*</li>', html)
    if m_opt and len(reds_500) >= 5 and len(blues_500) >= 2:
        yp = split_issue(m_opt.group(1))
        if yp:
            nums = [int(x) for x in reds_500[:5]] + [int(x) for x in blues_500[:2]]
            if (
                all(1 <= nums[i] <= 35 for i in range(5))
                and all(1 <= nums[i] <= 12 for i in range(5, 7))
            ):
                return {"year": yp[0], "period": yp[1], "numbers": nums}

    # kaijiang：shtml/dlt/26100 + ball_red/blue
    m_iss = re.search(r"dlt/(\d{5,7})", html)
    if m_iss and len(reds_500) >= 5 and len(blues_500) >= 2:
        yp = split_issue(m_iss.group(1))
        if yp:
            nums = [int(x) for x in reds_500[:5]] + [int(x) for x in blues_500[:2]]
            if (
                all(1 <= nums[i] <= 35 for i in range(5))
                and all(1 <= nums[i] <= 12 for i in range(5, 7))
            ):
                return {"year": yp[0], "period": yp[1], "numbers": nums}

    # 彩经网
    m_span = re.search(
        r'<div class="kj_data"[^>]*>[\s\S]*?<span>(20\d{5})',
        html,
    )
    idx = html.find('class="xin_kjinfo"')
    if m_span is not None and idx != -1:
        end = html.find('class="xin_kjshape"', idx)
        chunk = html[idx : end if end != -1 else idx + 4500]
        reds_c = re.findall(r'<span class="qiu_red">(\d{1,2})</span>', chunk)
        blues_c = re.findall(r'<span class="qiu_blue">(\d{1,2})</span>', chunk)
        if len(reds_c) >= 5 and len(blues_c) >= 2:
            yp = split_issue(m_span.group(1))
            if yp:
                nums = [int(x) for x in reds_c[:5]] + [int(x) for x in blues_c[:2]]
                if (
                    all(1 <= nums[i] <= 35 for i in range(5))
                    and all(1 <= nums[i] <= 12 for i in range(5, 7))
                ):
                    return {"year": yp[0], "period": yp[1], "numbers": nums}

    return None


def parse_latest_kl8(html: str) -> dict | None:
    rec = parse_mobile_expect_opencode(html, "kl8")
    if rec:
        return rec

    period_match = re.search(r"快乐8\s*[第]?\s*(\d{7})", html)
    if not period_match:
        period_match = re.search(r"/shtml/kl8/(\d{7})", html)
    if not period_match:
        period_match = re.search(r"(\d{4})(\d{3})\s*期", html)
        if period_match:
            year, period = period_match.group(1), period_match.group(2).zfill(3)
        else:
            return None
    else:
        yp = split_issue(period_match.group(1))
        if not yp:
            return None
        year, period = yp

    nums: list[int] = []
    numbers_match = re.search(r"开奖号码[：:]\s*([\d\s\-—－−]+)", html)
    if numbers_match:
        for num_str in re.findall(r"\d+", numbers_match.group(1)):
            n = int(num_str)
            if 1 <= n <= 80 and n not in nums:
                nums.append(n)
                if len(nums) >= 20:
                    break

    if len(nums) != 20:
        soup = BeautifulSoup(html, "html.parser")
        nums = []
        for ball in soup.select("li.ball_orange, li.ball_red, li.ball, span.ball"):
            text = ball.get_text(strip=True)
            if re.match(r"^\d{1,2}$", text):
                n = int(text)
                if 1 <= n <= 80 and n not in nums:
                    nums.append(n)
                    if len(nums) >= 20:
                        break

    if len(nums) != 20:
        return None
    return {"year": year, "period": period, "numbers": sorted(nums)}


PARSERS = {
    "ssq": parse_latest_ssq,
    "3d": parse_latest_3d,
    "kl8": parse_latest_kl8,
    "dlt": parse_latest_dlt,
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
    failed = []

    for key, (filename, var_name, comment) in LOTTERY_FILES.items():
        urls = URLS[key]
        parse_fn = PARSERS[key]
        path = lottery_dir / filename

        rec = None
        for url in urls:
            print(f"[{key}] fetch {url}")
            html = fetch_html(url)
            if not html:
                print("  no html")
                continue
            rec = parse_fn(html)
            if rec:
                print("  parsed OK")
                break
            print(
                "  parse failed, try next URL"
                if len(urls) > 1
                else "  parse failed"
            )

        if not rec:
            print(f"  skip {key}: parse latest failed for all URLs")
            failed.append(key)
            continue
        print(f"  latest: {rec['year']} {rec['period']}")

        data = load_lottery_js(path)
        if merge_record(data, rec):
            save_lottery_js(path, data, var_name, comment)
            updated.append(f"lottery/{filename}")
            print(f"  merged -> {path}")
        else:
            print("  no new record")

    if updated:
        print("Updated:", ", ".join(updated))
    else:
        print("No files updated.")

    if failed:
        print("Parse failed:", ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
