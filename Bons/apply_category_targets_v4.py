#!/usr/bin/env python3
"""v4: fix G2/G3 — wrong guard + middle-dot literal."""
import os, sys

TARGET = r"C:\Users\KamalSAGUEM\OneDrive - Beyond believers\Bureau\Rehab app ( planner) - Copie\rigab_app\index.html"
DOT = "·"  # the actual character

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

    # G2: th — guard on the literal targets-page string
    if "else if (scope === 'categories')   table += '<th>Category</th>'" not in src:
        src = must_replace_once(
            src,
            "  else if (scope === 'client-store') table += '<th>Client</th><th>Store</th>';\n  table += '<th class=\"num\" style=\"width:160px;\">Target</th></tr></thead><tbody>';",
            "  else if (scope === 'client-store') table += '<th>Client</th><th>Store</th>';\n  else if (scope === 'categories')   table += '<th>Category</th>';\n  else if (scope === 'store-category') table += '<th>Store</th><th>Category</th>';\n  table += '<th class=\"num\" style=\"width:160px;\">Target</th></tr></thead><tbody>';",
            "G2"
        )
        changed = True; print("[OK] G2")
    else: print("[skip] G2")

    # G3: td — use the LITERAL middle-dot character (not the escape)
    if "else if (scope === 'categories')   table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(r.name)" not in src:
        anchor = "    else if (scope === 'client-store') table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(gmvDisplayName(r.phone)) + '</div><div class=\"gmv-seller-meta\">' + escapeHtml(r.seller || '') + ' " + DOT + " ' + escapeHtml(r.phone) + '</div></td><td>' + escapeHtml(r.store) + '</td>';"
        replacement = anchor + "\n    else if (scope === 'categories')   table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(r.name) + '</div></td>';\n    else if (scope === 'store-category') table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(r.store) + '</div></td><td>' + escapeHtml(r.category) + '</td>';"
        src = must_replace_once(src, anchor, replacement, "G3")
        changed = True; print("[OK] G3")
    else: print("[skip] G3")

    # G4: stores chip
    if "|| scope === 'store-category')" not in src:
        src = must_replace_once(
            src,
            "  const showStoresChip   = (scope === 'stores'  || scope === 'seller-store' || scope === 'client-store');",
            "  const showStoresChip   = (scope === 'stores'  || scope === 'seller-store' || scope === 'client-store' || scope === 'store-category');",
            "G4"
        )
        changed = True; print("[OK] G4")
    else: print("[skip] G4")

    # I: clear-period
    if "storesByClient: {}, categories: {}, categoriesByStore: {}, global: 0" not in src:
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
    print("\nDone. Hard-refresh.")

if __name__ == '__main__':
    main()
