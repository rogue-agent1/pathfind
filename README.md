# pathfind

Fast file finder with glob, regex, size, age, and content filters.

## Usage

```bash
# Find Python files modified in last hour
python3 pathfind.py find . -e py --newer 1h -l

# Find files containing text
python3 pathfind.py find src -c "TODO" --stats

# Find duplicate files
python3 pathfind.py dupes ~/Documents

# Find largest files
python3 pathfind.py largest . -c 10
```

## Features

- Glob, regex, and extension matching
- Size and age filters
- Content search
- Duplicate detection (MD5)
- Largest file finder
- Long format with sizes and dates
- Hidden file and depth control
- Zero dependencies
