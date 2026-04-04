#!/usr/bin/env python3
"""pathfind - Fast file finder with glob, regex, and filter support.

Find files by name, extension, size, age, and content. Zero dependencies.
"""

import argparse
import os
import re
import sys
import time
import fnmatch
from datetime import datetime


def human_size(n: int) -> str:
    for u in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.1f}{u}" if u != "B" else f"{n}{u}"
        n /= 1024
    return f"{n:.1f}PB"


def parse_size(s: str) -> int:
    units = {"b": 1, "k": 1024, "kb": 1024, "m": 1024**2, "mb": 1024**2,
             "g": 1024**3, "gb": 1024**3, "t": 1024**4, "tb": 1024**4}
    s = s.strip().lower()
    for suffix, mult in sorted(units.items(), key=lambda x: -len(x[0])):
        if s.endswith(suffix):
            return int(float(s[:-len(suffix)]) * mult)
    return int(s)


def parse_age(s: str) -> float:
    """Parse age string like '1h', '30m', '7d' into seconds."""
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    s = s.strip().lower()
    if s[-1] in units:
        return float(s[:-1]) * units[s[-1]]
    return float(s)


def find_files(root, name=None, ext=None, regex=None, min_size=None, max_size=None,
               newer_than=None, older_than=None, contains=None, ftype=None,
               max_depth=None, hidden=False, ignore_dirs=None):
    ignore = ignore_dirs or {".git", "node_modules", "__pycache__", ".venv"}
    now = time.time()
    root = os.path.abspath(root)
    root_depth = root.rstrip(os.sep).count(os.sep)

    for dirpath, dirnames, filenames in os.walk(root):
        depth = dirpath.rstrip(os.sep).count(os.sep) - root_depth
        if max_depth is not None and depth >= max_depth:
            dirnames.clear()
            continue

        if not hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        dirnames[:] = [d for d in dirnames if d not in ignore]

        entries = filenames
        if ftype == "d":
            entries = dirnames
        elif ftype == "f":
            entries = filenames
        elif ftype is None:
            entries = filenames + dirnames

        for fname in entries:
            path = os.path.join(dirpath, fname)
            if not hidden and fname.startswith("."):
                continue

            if name and not fnmatch.fnmatch(fname, name):
                continue
            if ext and not fname.endswith(f".{ext.lstrip('.')}"):
                continue
            if regex and not re.search(regex, fname):
                continue

            try:
                st = os.stat(path)
            except OSError:
                continue

            if ftype == "f" and not os.path.isfile(path):
                continue
            if ftype == "d" and not os.path.isdir(path):
                continue

            if min_size is not None and st.st_size < min_size:
                continue
            if max_size is not None and st.st_size > max_size:
                continue
            if newer_than is not None and (now - st.st_mtime) > newer_than:
                continue
            if older_than is not None and (now - st.st_mtime) < older_than:
                continue

            if contains:
                try:
                    with open(path, "r", errors="ignore") as f:
                        if contains not in f.read():
                            continue
                except (OSError, IsADirectoryError):
                    continue

            yield path, st


def cmd_find(args):
    count = 0
    total_size = 0
    for path, st in find_files(
        args.root, name=args.name, ext=args.ext, regex=args.regex,
        min_size=parse_size(args.min_size) if args.min_size else None,
        max_size=parse_size(args.max_size) if args.max_size else None,
        newer_than=parse_age(args.newer) if args.newer else None,
        older_than=parse_age(args.older) if args.older else None,
        contains=args.contains, ftype=args.type, max_depth=args.depth,
        hidden=args.hidden,
    ):
        count += 1
        total_size += st.st_size
        if args.long:
            mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
            print(f"{human_size(st.st_size):>8}  {mtime}  {path}")
        else:
            print(path)
        if args.limit and count >= args.limit:
            break

    if args.stats:
        print(f"\n{count} files, {human_size(total_size)} total", file=sys.stderr)


def cmd_dupes(args):
    """Find duplicate files by size then content hash."""
    import hashlib
    by_size = {}
    for path, st in find_files(args.root, ftype="f", max_depth=args.depth, hidden=args.hidden):
        by_size.setdefault(st.st_size, []).append(path)

    groups = 0
    wasted = 0
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_hash = {}
        for p in paths:
            try:
                h = hashlib.md5(open(p, "rb").read()).hexdigest()
                by_hash.setdefault(h, []).append(p)
            except OSError:
                pass
        for h, dups in by_hash.items():
            if len(dups) < 2:
                continue
            groups += 1
            wasted += size * (len(dups) - 1)
            print(f"\n--- Group {groups} ({human_size(size)} each, {len(dups)} copies) ---")
            for d in dups:
                print(f"  {d}")

    print(f"\n{groups} duplicate groups, {human_size(wasted)} wasted", file=sys.stderr)


def cmd_largest(args):
    files = []
    for path, st in find_files(args.root, ftype="f", max_depth=args.depth, hidden=args.hidden):
        files.append((st.st_size, path))
    files.sort(reverse=True)
    n = args.count or 20
    for size, path in files[:n]:
        print(f"{human_size(size):>8}  {path}")


def main():
    p = argparse.ArgumentParser(description="Fast file finder")
    sub = p.add_subparsers(dest="cmd")

    fp = sub.add_parser("find", help="Find files with filters")
    fp.add_argument("root", nargs="?", default=".", help="Search root")
    fp.add_argument("-n", "--name", help="Glob pattern for filename")
    fp.add_argument("-e", "--ext", help="File extension filter")
    fp.add_argument("-r", "--regex", help="Regex pattern for filename")
    fp.add_argument("--min-size", help="Minimum file size (e.g. 1M)")
    fp.add_argument("--max-size", help="Maximum file size")
    fp.add_argument("--newer", help="Modified within (e.g. 1h, 7d)")
    fp.add_argument("--older", help="Modified before (e.g. 30d)")
    fp.add_argument("-c", "--contains", help="File contains text")
    fp.add_argument("-t", "--type", choices=["f", "d"], help="f=files, d=dirs")
    fp.add_argument("-d", "--depth", type=int, help="Max directory depth")
    fp.add_argument("-l", "--long", action="store_true", help="Long format")
    fp.add_argument("--hidden", action="store_true", help="Include hidden")
    fp.add_argument("--stats", action="store_true", help="Show summary stats")
    fp.add_argument("--limit", type=int, help="Max results")

    dp = sub.add_parser("dupes", help="Find duplicate files")
    dp.add_argument("root", nargs="?", default=".")
    dp.add_argument("-d", "--depth", type=int)
    dp.add_argument("--hidden", action="store_true")

    lp = sub.add_parser("largest", help="Find largest files")
    lp.add_argument("root", nargs="?", default=".")
    lp.add_argument("-c", "--count", type=int, default=20)
    lp.add_argument("-d", "--depth", type=int)
    lp.add_argument("--hidden", action="store_true")

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)
    {"find": cmd_find, "dupes": cmd_dupes, "largest": cmd_largest}[args.cmd](args)


if __name__ == "__main__":
    main()
