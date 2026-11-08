#!/usr/bin/env python3
"""把记忆类的 Markdown 拍一份快照，留 N 份。

只复制，不删原文件；同一分钟跑两次会跳过。
用法：
    python backup-memory.py --root "D:\\mei 11.2"          # 拍一份
    python backup-memory.py --root "D:\\mei 11.2" --list   # 看已有快照
文件清单可用 --files 覆盖（相对 root，逗号分隔）。
"""
from __future__ import annotations

import argparse
import datetime as _dt
import shutil
from pathlib import Path

DEFAULT_FILES = ["记忆.md", "纪事.md", "读记.md", "想做.md", "立场.md", "书单.md"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="工作区根目录")
    ap.add_argument("--out", default="", help="快照放哪（默认 <root>/outputs/backup）")
    ap.add_argument("--files", default="", help="逗号分隔的文件名，相对 root")
    ap.add_argument("--keep", type=int, default=60, help="保留份数")
    ap.add_argument("--list", action="store_true", help="列已有快照")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    out = Path(a.out) if a.out else root / "outputs" / "backup"
    files = [x.strip() for x in a.files.split(",") if x.strip()] or DEFAULT_FILES

    snaps = sorted((p for p in out.glob("*") if p.is_dir()), key=lambda p: p.name) if out.exists() else []
    if a.list:
        if not snaps:
            print("还没有快照")
            return 0
        for d in snaps:
            fs = [p for p in d.rglob("*") if p.is_file()]
            size = sum(p.stat().st_size for p in fs) / 1024
            print(f"{d.name}  {len(fs)} 个文件  {size:.1f} KB")
        print(f"共 {len(snaps)} 份")
        return 0

    stamp = _dt.datetime.now().strftime("%Y-%m-%d-%H%M")
    dest = out / stamp
    if dest.exists():
        print(f"已有同名快照：{stamp}")
        return 0
    dest.mkdir(parents=True)

    copied, missing = 0, []
    for rel in files:
        src = root / rel
        if not src.exists():
            missing.append(rel)
            continue
        tgt = dest / rel
        tgt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, tgt)
        copied += 1
    size = sum(p.stat().st_size for p in dest.rglob("*") if p.is_file()) / 1024
    print(f"快照 {stamp}：{copied} 个文件，{size:.1f} KB")
    if missing:
        print("缺：" + "、".join(missing))

    now_snaps = sorted((p for p in out.glob("*") if p.is_dir()), key=lambda p: p.name)
    for old in now_snaps[: max(0, len(now_snaps) - a.keep)]:
        shutil.rmtree(old)
        print(f"删旧快照：{old.name}")
    return 0 if copied else 1


if __name__ == "__main__":
    raise SystemExit(main())
