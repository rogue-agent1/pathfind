#!/usr/bin/env python3
"""pathfind - Find files with powerful filters.

One file. Zero deps. Finds files.

Usage:
  pathfind.py . --name "*.py"            → find Python files
  pathfind.py . --ext py js ts           → by extensions
  pathfind.py . --size +1M               → files over 1MB
  pathfind.py . --modified 7d            → modified in last 7 days
  pathfind.py . --empty                  → empty files
  pathfind.py . --name "*.log" --exec rm → find and execute
"""

import argparse
import fnmatch
import os
import subprocess
import sys
import time


SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.tox'}


def parse_size(s: str) -> int:
    """Parse size like +1M, -500K, 1G."""
    s = s.lstrip('+-')
    multipliers = {'b': 1, 'k': 1024, 'm': 1024**2, 'g': 1024**3}
    if s[-1].lower() in multipliers:
        return int(float(s[:-1]) * multipliers[s[-1].lower()])
    return int(s)


def parse_age(s: str) -> float:
    """Parse age like 7d, 2h, 30m."""
    units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}
    if s[-1].lower() in units:
        return float(s[:-1]) * units[s[-1].lower()]
    return float(s)


def matches(path: str, args) -> bool:
    name = os.path.basename(path)
    
    if args.name and not any(fnmatch.fnmatch(name, p) for p in args.name):
        return False
    
    if args.ext:
        _, ext = os.path.splitext(name)
        if ext.lstrip('.').lower() not in [e.lstrip('.').lower() for e in args.ext]:
            return False

    if args.size:
        try:
            sz = os.path.getsize(path)
        except OSError:
            return False
        size_str = args.size
        target = parse_size(size_str)
        if size_str.startswith('+') and sz < target:
            return False
        elif size_str.startswith('-') and sz > target:
            return False

    if args.modified:
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            return False
        age = time.time() - mtime
        max_age = parse_age(args.modified)
        if age > max_age:
            return False

    if args.empty:
        try:
            if os.path.getsize(path) != 0:
                return False
        except OSError:
            return False

    if args.contains:
        try:
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
            if args.contains not in content:
                return False
        except (OSError, UnicodeDecodeError):
            return False

    return True


def find_files(roots: list[str], args) -> list[str]:
    results = []
    for root in roots:
        if os.path.isfile(root):
            if matches(root, args):
                results.append(root)
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            if not args.hidden:
                dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in SKIP_DIRS]
            if args.type in ('f', None):
                for f in filenames:
                    if not args.hidden and f.startswith('.'):
                        continue
                    full = os.path.join(dirpath, f)
                    if matches(full, args):
                        results.append(full)
            if args.type == 'd':
                for d in dirnames:
                    full = os.path.join(dirpath, d)
                    results.append(full)
    return results


def fmt_size(size: int) -> str:
    for unit in ['B', 'K', 'M', 'G']:
        if size < 1024:
            return f"{size:>6.1f}{unit}" if unit != 'B' else f"{size:>6}{unit}"
        size /= 1024
    return f"{size:.1f}T"


def main():
    parser = argparse.ArgumentParser(description="Find files with powerful filters")
    parser.add_argument("paths", nargs="*", default=["."])
    parser.add_argument("--name", "-n", action="append", help="Glob pattern")
    parser.add_argument("--ext", "-e", nargs="+", help="File extensions")
    parser.add_argument("--size", "-s", help="Size filter (+1M, -500K)")
    parser.add_argument("--modified", "-m", help="Modified within (7d, 2h)")
    parser.add_argument("--empty", action="store_true", help="Empty files only")
    parser.add_argument("--contains", "-c", help="Files containing text")
    parser.add_argument("--type", "-t", choices=["f", "d"], help="f=files, d=dirs")
    parser.add_argument("--hidden", action="store_true", help="Include hidden")
    parser.add_argument("--long", "-l", action="store_true", help="Long format with size/date")
    parser.add_argument("--exec", dest="execute", help="Command to run on each file")
    parser.add_argument("--count", action="store_true", help="Just count")

    args = parser.parse_args()
    results = find_files(args.paths, args)
    results.sort()

    if args.count:
        print(len(results))
        return 0

    if args.execute:
        for path in results:
            cmd = args.execute.replace('{}', path)
            print(f"  → {cmd}", file=sys.stderr)
            subprocess.run(cmd, shell=True)
        return 0

    for path in results:
        if args.long:
            try:
                stat = os.stat(path)
                size = fmt_size(stat.st_size)
                mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))
                print(f"  {size}  {mtime}  {path}")
            except OSError:
                print(f"  {'?':>7}  {'?':>16}  {path}")
        else:
            print(path)

    print(f"\n{len(results)} files found", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
