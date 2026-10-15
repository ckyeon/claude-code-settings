import csv
import sys


def main(path):
    rows = list(csv.DictReader(open(path)))
    total = 0
    for r in rows:
        total = total + float(r["amount"])
    print("total", total)
    by_cat = {}
    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + float(r["amount"])
    for k in by_cat:
        print(k, by_cat[k])


main(sys.argv[1])
