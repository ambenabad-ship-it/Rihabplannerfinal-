#!/usr/bin/env python3
"""v2: fixes the ambiguous anchor in step D and re-applies everything."""
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

    # A: bucket shape
    if "categoriesByStore" not in src:
        src = must_replace_once(
            src,
            "    gmv.targets[k] = { sellers: {}, clients: {}, stores: {}, storesBySeller: {}, storesByClient: {} };\n  }\n  if (!gmv.targets[k].sellers) gmv.targets[k].sellers = {};\n  if (!gmv.targets[k].clients) gmv.targets[k].clients = {};\n  if (!gmv.targets[k].stores)  gmv.targets[k].stores  = {};\n  if (!gmv.targets[k].storesBySeller) gmv.targets[k].storesBySeller = {};\n  if (!gmv.targets[k].storesByClient) gmv.targets[k].storesByClient = {};",
            "    gmv.targets[k] = { sellers: {}, clients: {}, stores: {}, storesBySeller: {}, storesByClient: {}, categories: {}, categoriesByStore: {} };\n  }\n  if (!gmv.targets[k].sellers) gmv.targets[k].sellers = {};\n  if (!gmv.targets[k].clients) gmv.targets[k].clients = {};\n  if (!gmv.targets[k].stores)  gmv.targets[k].stores  = {};\n  if (!gmv.targets[k].storesBySeller) gmv.targets[k].storesBySeller = {};\n  if (!gmv.targets[k].storesByClient) gmv.targets[k].storesByClient = {};\n  if (!gmv.targets[k].categories) gmv.targets[k].categories = {};\n  if (!gmv.targets[k].categoriesByStore) gmv.targets[k].categoriesByStore = {};",
            "A"
        )
        changed = True; print("[OK] A")
    else: print("[skip] A")

    # B: scope dropdown
    if "store-category" not in src:
        if "Clients × Stores" in src:
            src = must_replace_once(
                src,
                "  { id: 'client-store',  label: 'Clients × Stores' }",
                "  { id: 'client-store',  label: 'Clients × Stores' },\n  { id: 'categories',    label: 'Categories'         },\n  { id: 'store-category',label: 'Stores × Categories' }",
                "B"
            )
        else:
            src = must_replace_once(
                src,
                "  { id: 'client-store',  label: 'Clients \\u00d7 Stores' }",
                "  { id: 'client-store',  label: 'Clients \\u00d7 Stores' },\n  { id: 'categories',    label: 'Categories'         },\n  { id: 'store-category',label: 'Stores \\u00d7 Categories' }",
                "B"
            )
        changed = True; print("[OK] B")
    else: print("[skip] B")

    # C: gmvAllCategories helper
    if "function gmvAllCategories" not in src:
        helper = (
            "function gmvAllCategories() {\n"
            "  const set = new Set();\n"
            "  Object.values(gmv.productCategories || {}).forEach(v => {\n"
            "    if (v && v.category) set.add(v.category);\n"
            "  });\n"
            "  return [...set].sort((a, b) => a.localeCompare(b));\n"
            "}\n"
            "\n"
        )
        src = must_replace_once(src, "function gmvUniqueSellers() {", helper + "function gmvUniqueSellers() {", "C")
        changed = True; print("[OK] C")
    else: print("[skip] C")

    # D: gmvFlatRows — use comment anchor that's UNIQUE to gmvFlatRows
    if "scope === 'categories'" not in src:
        src = must_replace_once(
            src,
            "  if (scope === 'client-store') {\n    // Build (client, store) cells from orders so we only show the pairs",
            "  if (scope === 'categories') {\n"
            "    const cats = gmvAllCategories();\n"
            "    return cats.map(c => ({ kind: 'category', category: c, name: c, target: (bucket.categories && bucket.categories[c]) || 0 }));\n"
            "  }\n"
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
            "  if (scope === 'client-store') {\n    // Build (client, store) cells from orders so we only show the pairs",
            "D"
        )
        changed = True; print("[OK] D")
    else: print("[skip] D")

    # E: caps
    if "scope === 'store-category'" not in src:
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
        changed = True; print("[OK] E")
    else: print("[skip] E")

    # F: save
    if "b.categories[row.category]" not in src:
        src = must_replace_once(
            src,
            "  if (scope === 'client-store') {\n    if (!b.storesByClient[row.phone]) b.storesByClient[row.phone] = {};\n    b.storesByClient[row.phone][row.store] = v;\n  }\n}",
            "  if (scope === 'client-store') {\n    if (!b.storesByClient[row.phone]) b.storesByClient[row.phone] = {};\n    b.storesByClient[row.phone][row.store] = v;\n  }\n"
            "  if (scope === 'categories') {\n    if (!b.categories) b.categories = {};\n    b.categories[row.category] = v;\n  }\n"
            "  if (scope === 'store-category') {\n    if (!b.categoriesByStore) b.categoriesByStore = {};\n    if (!b.categoriesByStore[row.store]) b.categoriesByStore[row.store] = {};\n    b.categoriesByStore[row.store][row.category] = v;\n  }\n}",
            "F"
        )
        changed = True; print("[OK] F")
    else: print("[skip] F")

    # G: render header + cells + chips
    if "scope === 'store-category')" not in src or "<th>Category</th>" not in src:
        if "scope === 'store-category')" not in src:
            src = must_replace_once(
                src,
                "  const colCount = (scope === 'seller-store' || scope === 'client-store') ? 4 : 3;",
                "  const colCount = (scope === 'seller-store' || scope === 'client-store' || scope === 'store-category') ? 4 : 3;",
                "G1"
            )
        if "<th>Category</th>" not in src:
            src = must_replace_once(
                src,
                "  else if (scope === 'client-store') table += '<th>Client</th><th>Store</th>';\n  table += '<th class=\"num\" style=\"width:160px;\">Target</th></tr></thead><tbody>';",
                "  else if (scope === 'client-store') table += '<th>Client</th><th>Store</th>';\n  else if (scope === 'categories')   table += '<th>Category</th>';\n  else if (scope === 'store-category') table += '<th>Store</th><th>Category</th>';\n  table += '<th class=\"num\" style=\"width:160px;\">Target</th></tr></thead><tbody>';",
                "G2"
            )
        if "scope === 'categories')   table += '<td>" not in src:
            src = must_replace_once(
                src,
                "    else if (scope === 'client-store') table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(gmvDisplayName(r.phone)) + '</div><div class=\"gmv-seller-meta\">' + escapeHtml(r.seller || '') + ' \\u00b7 ' + escapeHtml(r.phone) + '</div></td><td>' + escapeHtml(r.store) + '</td>';",
                "    else if (scope === 'client-store') table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(gmvDisplayName(r.phone)) + '</div><div class=\"gmv-seller-meta\">' + escapeHtml(r.seller || '') + ' \\u00b7 ' + escapeHtml(r.phone) + '</div></td><td>' + escapeHtml(r.store) + '</td>';\n    else if (scope === 'categories')   table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(r.name) + '</div></td>';\n    else if (scope === 'store-category') table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(r.store) + '</div></td><td>' + escapeHtml(r.category) + '</td>';",
                "G3"
            )
        if "scope === 'store-category')" not in src.split("showStoresChip")[1] if "showStoresChip" in src else False:
            pass
        if "|| scope === 'store-category'" not in src:
            src = must_replace_once(
                src,
                "  const showStoresChip   = (scope === 'stores'  || scope === 'seller-store' || scope === 'client-store');",
                "  const showStoresChip   = (scope === 'stores'  || scope === 'seller-store' || scope === 'client-store' || scope === 'store-category');",
                "G4"
            )
        changed = True; print("[OK] G")
    else: print("[skip] G")

    # I: clear-period
    if "categories: {}, categoriesByStore: {}" not in src:
        src = must_replace_once(
            src,
            "      gmv.targets[k] = { sellers: {}, clients: {}, stores: {}, storesBySeller: {}, storesByClient: {}, global: 0 };",
            "      gmv.targets[k] = { sellers: {}, clients: {}, stores: {}, storesBySeller: {}, storesByClient: {}, categories: {}, categoriesByStore: {}, global: 0 };",
            "I"
        )
        changed = True; print("[OK] I")
    else: print("[skip] I")

    if not changed:
        print("\nAlready fully patched.")
        return
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("\nDone. Hard-refresh — Targets dropdown now has 'Categories' and 'Stores \\u00d7 Categories'.")

if __name__ == '__main__':
    main()
