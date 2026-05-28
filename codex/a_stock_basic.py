#!/usr/bin/env python
"""Small Codex-friendly entrypoint for common no-key A-share lookups."""

import argparse
import json
import sys
import urllib.request

import requests


UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
HTTP = requests.Session()
DIRECT_HTTP = requests.Session()
DIRECT_HTTP.trust_env = False


def normalize_code(code: str) -> str:
    code = code.strip().lower()
    if code.startswith(("sh", "sz", "bj")):
        return code[2:]
    if "." in code:
        return code.split(".", 1)[0]
    return code


def market_prefix(code: str) -> str:
    code = normalize_code(code)
    if code.startswith(("6", "9")):
        return "sh"
    if code.startswith("8"):
        return "bj"
    return "sz"


def tencent_quote(codes: list[str]) -> dict[str, dict]:
    prefixed = [f"{market_prefix(c)}{normalize_code(c)}" for c in codes]
    url = "https://qt.gtimg.cn/q=" + ",".join(prefixed)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=10).read().decode("gbk", errors="replace")

    result = {}
    for line in data.strip().split(";"):
        if not line.strip() or "=" not in line or '"' not in line:
            continue
        key = line.split("=")[0].split("_")[-1]
        vals = line.split('"')[1].split("~")
        if len(vals) < 53:
            continue
        code = key[2:]
        result[code] = {
            "name": vals[1],
            "price": _float(vals[3]),
            "last_close": _float(vals[4]),
            "open": _float(vals[5]),
            "change_amt": _float(vals[31]),
            "change_pct": _float(vals[32]),
            "high": _float(vals[33]),
            "low": _float(vals[34]),
            "amount_wan": _float(vals[37]),
            "turnover_pct": _float(vals[38]),
            "pe_ttm": _float(vals[39]),
            "amplitude_pct": _float(vals[43]),
            "mcap_yi": _float(vals[44]),
            "float_mcap_yi": _float(vals[45]),
            "pb": _float(vals[46]),
            "limit_up": _float(vals[47]),
            "limit_down": _float(vals[48]),
            "vol_ratio": _float(vals[49]),
            "pe_static": _float(vals[52]),
        }
    return result


def eastmoney_stock_info(code: str) -> dict:
    code = normalize_code(code)
    market_code = 1 if code.startswith(("6", "9")) else 0
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f57,f58,f84,f85,f127,f116,f117,f189,f43",
        "secid": f"{market_code}.{code}",
    }
    r = eastmoney_get(url, params=params, timeout=10)
    r.raise_for_status()
    d = r.json().get("data") or {}
    return {
        "code": d.get("f57", ""),
        "name": d.get("f58", ""),
        "industry": d.get("f127", ""),
        "total_shares": d.get("f84", 0),
        "float_shares": d.get("f85", 0),
        "mcap": d.get("f116", 0),
        "float_mcap": d.get("f117", 0),
        "list_date": str(d.get("f189", "")),
        "price": d.get("f43", 0),
    }


def industry_comparison(top_n: int = 10) -> dict:
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fs": "m:90+t:2",
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
    }
    r = eastmoney_get(url, params=params, timeout=15)
    r.raise_for_status()
    items = (r.json().get("data") or {}).get("diff") or []
    rows = []
    for i, item in enumerate(items):
        rows.append(
            {
                "rank": i + 1,
                "name": item.get("f14", ""),
                "change_pct": item.get("f3", 0),
                "code": item.get("f12", ""),
                "up_count": item.get("f104", 0),
                "down_count": item.get("f105", 0),
                "leader": item.get("f140", ""),
                "leader_change": item.get("f136", 0),
            }
        )
    return {"top": rows[:top_n], "bottom": rows[-top_n:], "total": len(rows)}


def eastmoney_get(url: str, params: dict, timeout: int):
    try:
        return HTTP.get(url, params=params, headers={"User-Agent": UA}, timeout=timeout)
    except requests.RequestException:
        return DIRECT_HTTP.get(url, params=params, headers={"User-Agent": UA}, timeout=timeout)


def _float(value):
    try:
        return float(value) if value not in ("", None, "-") else 0.0
    except (TypeError, ValueError):
        return 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="A-share basic data helper for Codex.")
    sub = parser.add_subparsers(dest="command", required=True)

    quote = sub.add_parser("quote", help="Tencent real-time quote.")
    quote.add_argument("codes", nargs="+")

    info = sub.add_parser("info", help="Eastmoney stock profile.")
    info.add_argument("code")

    industry = sub.add_parser("industry", help="Eastmoney industry ranking.")
    industry.add_argument("--top", type=int, default=10)

    args = parser.parse_args()
    if args.command == "quote":
        output = tencent_quote(args.codes)
    elif args.command == "info":
        output = eastmoney_stock_info(args.code)
    elif args.command == "industry":
        output = industry_comparison(args.top)
    else:
        parser.error("unknown command")

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
