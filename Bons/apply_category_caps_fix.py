#!/usr/bin/env python3
"""Adds the missing caps for Categories and Store x Category."""
import os, sys
TARGET = r"C:\Users\KamalSAGUEM\OneDrive - Beyond believers\Bureau\Rehab app ( planner) - Copie\rigab_app\index.html"

def must_replace_once(src, anchor, replacement, label):
    n = src.count(anchor)
    if n == 0: raise SystemExit("[FAIL] anchor not found for " + label)
    if n > 1:  raise SystemExit("[FAIL] anchor appears " + str(n) + "x for " + label)
    return src.replace(anchor, replacement, 1)

def main():
    with open(TARGET, 'r', encoding='utf-8') as f:
        src = f.read()
    if "Object.keys(bucket.categoriesByStore || {})" in src:
        print("[skip] caps already there"); return
    src = must_replace_once(
        src,
        "  if (scope === 'client-store') {\n    const cliT = (bucket.clients && bucket.clients[row.phone]) || 0;",
        "  if (scope === 'categories') {\n"
        "    const globalT = (typeof bucket.global === 'number') ? bucket.global : 0;\n"
        "    const sum = Object.values(bucket.categories || {}).reduce((n, v) => n + (v || 0), 0);\n"
        "    return gmvBudgetCap(globalT, sum, row.target || 0);\n"
        "  }\n"
        "  if (scope === 'store-category') {\n"
        "    const storeT = (bucket.stores && bucket.stores[row.store]) || 0;\n"
        "    const catT   = (bucket.categories && bucket.categories[row.category]) || 0;\n"
        "    const storeCatsAll = Object.values((bucket.categoriesByStore && bucket.categoriesByStore[row.store]) || {}).reduce((n, v) => n + (v || 0), 0);\n"
        "    const catAcrossStores = Object.keys(bucket.categoriesByStore || {}).reduce((n, sN) => {\n"
        "      return n + ((bucket.categoriesByStore[sN] || {})[row.category] || 0);\n"
        "    }, 0);\n"
        "    return gmvBudgetCapMulti([\n"
        "      { parent: storeT, siblingsSumIncludingSelf: storeCatsAll, label: 'store' },\n"
        "      { parent: catT,   siblingsSumIncludingSelf: catAcrossStores, label: 'category' }\n"
        "    ], row.target || 0);\n"
        "  }\n"
        "  if (scope === 'client-store') {\n    const cliT = (bucket.clients && bucket.clients[row.phone]) || 0;",
        "caps"
    )
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] caps + room-left wired. Hard-refresh.")

if __name__ == '__main__':
    main()
