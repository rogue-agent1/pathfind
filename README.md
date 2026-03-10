# pathfind

Find files with powerful filters.

One file. Zero deps. Finds files.

## Usage

```bash
python3 pathfind.py . --name "*.py"
python3 pathfind.py . --ext py js ts
python3 pathfind.py . --size +1M -l
python3 pathfind.py . --modified 7d
python3 pathfind.py . --contains "TODO" --name "*.py"
python3 pathfind.py . --name "*.log" --exec "rm {}"
python3 pathfind.py . --empty --count
```

## Requirements

Python 3.8+. No dependencies.

## License

MIT
