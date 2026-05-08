#!/usr/bin/env python3
"""v6: anchor used \\u00d7 escape, not literal."""
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
        "  if (scope === 'store-category') {\n"
        "    const out = [];\n"
        "    const cats = gmvAllCategories();\n"
        "    stores.forEach(st => {\n"
        "      cats.forEach(ct => {\n"
        "        out.push({\n"
        "          kind: 'store-category', store: st, category: ct, name: st + ' \\u00d7 ' + ct,\n"
        "          target: ((bucket.categoriesByStore && bucket.categoriesByStore[st]) || {})[ct] || 0\n"
        "        });\n"
        "      });\n"
        "    });\n"
        "    return out;\n"
        "  }\n"
    )
    new = (
        "  if (scope === 'store-category') {\n"
        "    // Only (store, category) pairs that actually appear in orders.\n"
        "    const seen = {};\n"
        "    (gmv.orders || []).forEach(o => {\n"
        "      if (!o.store) return;\n"
        "      const ent = (gmv.productCategories || {})[o.productCode || ''];\n"
        "      const cat = ent && ent.category ? ent.category : null;\n"
        "      if (!cat) return;\n"
        "      const k = o.store + '|' + cat;\n"
        "      if (!seen[k]) seen[k] = { store: o.store, category: cat };\n"
        "    });\n"
        "    return Object.values(seen).map(r => ({\n"
        "      kind: 'store-category', store: r.store, category: r.category,\n"
        "      name: r.store + ' \\u00d7 ' + r.category,\n"
        "      target: ((bucket.categoriesByStore && bucket.categoriesByStore[r.store]) || {})[r.category] || 0\n"
        "    })).sort((a, b) => a.name.localeCompare(b.name));\n"
        "  }\n"
    )

    if "(store, category) pairs that actually appear in orders" in src:
        print("[skip] already done"); return
    src = must_replace_once(src, old, new, "store-category rows")
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] Hard-refresh.")

if __name__ == '__main__':
    main()
