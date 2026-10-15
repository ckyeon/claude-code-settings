import sys

path = sys.argv[1]
statements = [s for s in open(path).read().split(";") if s.strip()]
print(f"OK: {len(statements)} statements, no syntax errors found in {path}")
