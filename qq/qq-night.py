#!/usr/bin/env python3
"""夜里开关某个 QQ 群的接收：改 `~/.dsh/qq-bridge-config.json` 里那一行的「开」。

开 = false 时，桥对这一行**不收也不发**（配置留着，随时能打开）。
配合 dsh-qq-link 使用，不修改它的代码。

用法：
    python qq-night.py --off 645937444
    python qq-night.py --on 645937444
    python qq-night.py --status
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

CFG = Path(os.environ.get("DSH_HOME") or (Path.home() / ".dsh")) / "qq-bridge-config.json"


def load() -> dict:
    return json.loads(CFG.read_text("utf-8"))


def save(cfg: dict) -> None:
    tmp = CFG.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", "utf-8")
    tmp.replace(CFG)


def set_group(num: str, on: bool) -> str:
    cfg = load()
    hit = 0
    for row in cfg.get("绑定") or []:
        if row.get("类型") == "群" and str(row.get("号码")) == str(num):
            row["开"] = bool(on)
            hit += 1
    if not hit:
        return f"没有这个群的绑定：{num}"
    save(cfg)
    return f"{num} 接收{'打开' if on else '停掉'}（{hit} 行）"


def status() -> str:
    lines = []
    for row in load().get("绑定") or []:
        lines.append(f"{row.get('类型')} {row.get('号码')}: {'关' if row.get('开') is False else '开'}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--off", metavar="群号")
    g.add_argument("--on", metavar="群号")
    g.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        print(status())
        return 0
    print(set_group(a.off, False) if a.off else set_group(a.on, True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
