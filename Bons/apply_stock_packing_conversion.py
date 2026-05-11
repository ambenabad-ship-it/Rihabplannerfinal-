#!/usr/bin/env python3
"""Stock conversion: divide atomic stock by Package quantity when the product's Sell unit = PACKING."""
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
    if "sellUnit: sell," in src and "stockConvertedToPacking" in src:
        print("[skip] already done"); return

    # A: extend awalBuildLookup to carry sellUnit + pkgQty.
    if "sellUnit: sell," not in src:
        src = must_replace_once(
            src,
            "    lookup.set(code, {\n"
            "      name_ar:   awalClean(row['Arabic description']),\n"
            "      colisage,\n"
            "      bc_carton: awalClean(row['Package barcode']),\n"
            "      bc_unit:   awalClean(row['Atomic barcode']),\n"
            "      unit,\n"
            "    });",
            "    lookup.set(code, {\n"
            "      name_ar:   awalClean(row['Arabic description']),\n"
            "      colisage,\n"
            "      bc_carton: awalClean(row['Package barcode']),\n"
            "      bc_unit:   awalClean(row['Atomic barcode']),\n"
            "      unit,\n"
            "      sellUnit: sell,\n"
            "      pkgQty: pkgQty,\n"
            "    });",
            "A: extend lookup"
        )
        print("[OK] A: awalBuildLookup carries sellUnit + pkgQty")

    # B: apply conversion in the stock-loading loop.
    if "stockConvertedToPacking" not in src:
        old = (
            "  stock.forEach(s => {\n"
            "    const code = (s[sCode]||'').toString().trim();\n"
            "    if (!code) return;\n"
            "    const rawQ = parseFloat(s[sQty]);\n"
            "    const q = isFinite(rawQ) ? rawQ : 0;\n"
            "    if (q < 0) {\n"
            "      negativeStockCodes.push({ code, raw: q });\n"
            "      initialStock.set(code, (initialStock.get(code) || 0) + 0); // clamp to 0\n"
            "    } else {\n"
            "      initialStock.set(code, (initialStock.get(code) || 0) + q);\n"
            "    }\n"
            "  });"
        )
        new = (
            "  // Track how many rows we converted from atomic\\u2192packing so the operator\n"
            "  // gets a count in the summary. Conversion applies only when the\n"
            "  // Articles Matjar catalog has Sell unit = PACKING and a Package quantity.\n"
            "  let stockConvertedToPacking = 0;\n"
            "  stock.forEach(s => {\n"
            "    const code = (s[sCode]||'').toString().trim();\n"
            "    if (!code) return;\n"
            "    const rawQ = parseFloat(s[sQty]);\n"
            "    let q = isFinite(rawQ) ? rawQ : 0;\n"
            "    // Convert atomic stock to packing units when the product is sold per package.\n"
            "    const art = (typeof awalArticlesLookup !== 'undefined' && awalArticlesLookup) ? awalArticlesLookup.get(code) : null;\n"
            "    if (art && art.sellUnit === 'PACKING' && art.pkgQty && art.pkgQty > 0) {\n"
            "      q = Math.floor(q / art.pkgQty);\n"
            "      stockConvertedToPacking++;\n"
            "    }\n"
            "    if (q < 0) {\n"
            "      negativeStockCodes.push({ code, raw: q });\n"
            "      initialStock.set(code, (initialStock.get(code) || 0) + 0); // clamp to 0\n"
            "    } else {\n"
            "      initialStock.set(code, (initialStock.get(code) || 0) + q);\n"
            "    }\n"
            "  });"
        )
        src = must_replace_once(src, old, new, "B: conversion in stock loop")
        print("[OK] B: stock loop now converts atomic\\u2192packing")

    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("\nDone. Hard-refresh. Stock for PACKING products is now floor(atomic / packageQty).")

if __name__ == '__main__':
    main()
