#!/usr/bin/env python
"""Patch SkillHub's announcement-search CLI for the current dict response shape."""

from pathlib import Path


ROOT = Path.home() / ".codex" / "skills" / "announcement-search" / "scripts"
MAIN = ROOT / "__main__.py"


UNPACK_FUNCTION = '''
def unpack_search_result(search: AnnouncementSearch, result: Dict[str, Any], limit: int):
    if not result.get("success"):
        return False, [], result.get("error") or f"API调用失败，状态码: {result.get('status_code')}"

    raw_response = result.get("raw_response") or {}
    raw_items = raw_response.get("data") or []
    if not isinstance(raw_items, list):
        return False, [], "API响应 data 字段不是列表"

    return True, search._process_results(raw_items[:limit]), "OK"

'''


def main() -> int:
    if not MAIN.exists():
        raise SystemExit(f"announcement-search CLI not found: {MAIN}")

    text = MAIN.read_text(encoding="utf-8")
    if "def unpack_search_result(" not in text:
        marker = "\ndef display_results("
        if marker not in text:
            raise SystemExit("Could not find display_results marker")
        text = text.replace(marker, "\n" + UNPACK_FUNCTION + marker, 1)

    text = text.replace(
        "for query, (success, results, message) in batch_results.items():",
        "for query, result in batch_results.items():\n            success, results, message = unpack_search_result(search, result, args.limit)",
    )
    text = text.replace(
        "success, results, message = search.search(args.query, args.limit)",
        "result = search.search(args.query, args.limit)\n        success, results, message = unpack_search_result(search, result, args.limit)",
    )

    MAIN.write_text(text, encoding="utf-8")
    print(f"Patched {MAIN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
