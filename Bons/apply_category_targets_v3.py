#!/usr/bin/env python3
"""v3: applies the E (caps), G (UI), I (clear-period) blocks that v2 wrongly skipped."""
import os, sys

TARGET = r"C:\Users\KamalSAGUEM\OneDrive - Beyond believers\Bureau\Rehab app ( planner) - Copie\rigab_app\index.html"

def must_replace_once(src, anchor, replacement, label):
    n = src.count(anchor)
    if n == 0: raise SystemExit("[FAIL] anchor not found for " + label)
    if n > 1:  raise SystemExit("[FAIL] anchor appears " + str(n) + "x for " + label)
    return src.replace(anchor, replacement, 1)

def main():
    if not os.path.exists(TARGET):
        sys.exit("[FAIL] target not found: " + TARGET)
    with open(TARGET, 'r', encoding='utf-8') as f:
        src = f.read()
    changed = False

    # E: caps. Strong guard: the unique inner expression.
    if "Object.keys(bucket.categoriesByStore || {})" not in src:
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
            "E"
        )
        changed = True; print("[OK] E (caps)")
    else: print("[skip] E")

    # G1: colCount
    if "scope === 'store-category') ? 4" not in src:
        src = must_replace_once(
            src,
            "  const colCount = (scope === 'seller-store' || scope === 'client-store') ? 4 : 3;",
            "  const colCount = (scope === 'seller-store' || scope === 'client-store' || scope === 'store-category') ? 4 : 3;",
            "G1"
        )
        changed = True; print("[OK] G1 (colCount)")
    else: print("[skip] G1")

    # G2: th
    if "<th>Category</th>" not in src:
        src = must_replace_once(
            src,
            "  else if (scope === 'client-store') table += '<th>Client</th><th>Store</th>';\n  table += '<th class=\"num\" style=\"width:160px;\">Target</th></tr></thead><tbody>';",
            "  else if (scope === 'client-store') table += '<th>Client</th><th>Store</th>';\n  else if (scope === 'categories')   table += '<th>Category</th>';\n  else if (scope === 'store-category') table += '<th>Store</th><th>Category</th>';\n  table += '<th class=\"num\" style=\"width:160px;\">Target</th></tr></thead><tbody>';",
            "G2"
        )
        changed = True; print("[OK] G2 (header cells)")
    else: print("[skip] G2")

    # G3: td
    if "scope === 'categories')   table += '<td>" not in src:
        src = must_replace_once(
            src,
            "    else if (scope === 'client-store') table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(gmvDisplayName(r.phone)) + '</div><div class=\"gmv-seller-meta\">' + escapeHtml(r.seller || '') + ' \\u00b7 ' + escapeHtml(r.phone) + '</div></td><td>' + escapeHtml(r.store) + '</td>';",
            "    else if (scope === 'client-store') table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(gmvDisplayName(r.phone)) + '</div><div class=\"gmv-seller-meta\">' + escapeHtml(r.seller || '') + ' \\u00b7 ' + escapeHtml(r.phone) + '</div></td><td>' + escapeHtml(r.store) + '</td>';\n    else if (scope === 'categories')   table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(r.name) + '</div></td>';\n    else if (scope === 'store-category') table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(r.store) + '</div></td><td>' + escapeHtml(r.category) + '</td>';",
            "G3"
        )
        changed = True; print("[OK] G3 (data cells)")
    else: print("[skip] G3")

    # G4: stores chip extends to store-category
    if "|| scope === 'store-category')" not in src:
        src = must_replace_once(
            src,
            "  const showStoresChip   = (scope === 'stores'  || scope === 'seller-store' || scope === 'client-store');",
            "  const showStoresChip   = (scope === 'stores'  || scope === 'seller-store' || scope === 'client-store' || scope === 'store-category');",
            "G4"
        )
        changed = True; print("[OK] G4 (stores chip)")
    else: print("[skip] G4")

    # I: clear-period
    if "storesByClient: {}, categories: {}, categoriesByStore: {}, global: 0" not in src:
        src = must_replace_once(
            src,
            "      gmv.targets[k] = { sellers: {}, clients: {}, stores: {}, storesBySeller: {}, storesByClient: {}, global: 0 };",
            "      gmv.targets[k] = { sellers: {}, clients: {}, stores: {}, storesBySeller: {}, storesByClient: {}, categories: {}, categoriesByStore: {}, global: 0 };",
            "I"
        )
        changed = True; print("[OK] I (clear-period)")
    else: print("[skip] I")

    if not changed:
        print("\nAlready fully patched.")
        return
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("\nDone. Hard-refresh.")

if __name__ == '__main__':
    main()
