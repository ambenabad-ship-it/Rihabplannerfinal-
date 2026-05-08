#!/usr/bin/env python3
"""Make Category target OPTIONAL for Store x Category — only cap by Category when it's set."""
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

    old = (
        "    return gmvBudgetCapMulti([\n"
        "      { parent: storeT, siblingsSumIncludingSelf: storeCatsAll, label: 'store' },\n"
        "      { parent: catT,   siblingsSumIncludingSelf: catAcrossStores, label: 'category' }\n"
        "    ], row.target || 0);"
    )
    new = (
        "    // Store target is required; Category target is OPTIONAL — only adds a cap when set.\n"
        "    const constraints = [{ parent: storeT, siblingsSumIncludingSelf: storeCatsAll, label: 'store' }];\n"
        "    if (catT > 0) constraints.push({ parent: catT, siblingsSumIncludingSelf: catAcrossStores, label: 'category' });\n"
        "    return gmvBudgetCapMulti(constraints, row.target || 0);"
    )

    if "Store target is required; Category target is OPTIONAL" in src:
        print("[skip] already done"); return
    src = must_replace_once(src, old, new, "store-category optional cat")
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] Category target now optional. Hard-refresh.")

if __name__ == '__main__':
    main()
