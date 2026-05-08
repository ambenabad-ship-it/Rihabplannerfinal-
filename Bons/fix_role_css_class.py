#!/usr/bin/env python3
"""Backup hide via body class — gmvApplyRoleUI now also toggles 'gmv-is-viewer' on <body>."""
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
    if "gmv-is-viewer" in src:
        print("[skip] already done"); return

    # Add CSS rule + body class toggle.
    src = must_replace_once(
        src,
        "function gmvApplyRoleUI() {\n  const isCreator = gmvIsCreator();\n  const strip = document.getElementById('gmvDsStrip');\n  if (strip) strip.style.display = isCreator ? '' : 'none';",
        "function gmvApplyRoleUI() {\n  const isCreator = gmvIsCreator();\n  // Body class drives a CSS belt-and-braces hide of upload tiles.\n  document.body.classList.toggle('gmv-is-viewer', !!sbUser && !isCreator);\n  document.body.classList.toggle('gmv-is-creator', !!sbUser && isCreator);\n  const strip = document.getElementById('gmvDsStrip');\n  if (strip) strip.style.display = isCreator ? '' : 'none';",
        "body class toggle"
    )
    # Inject CSS into <head>
    src = must_replace_once(
        src,
        "</head>",
        "<style>\n  body.gmv-is-viewer #gmvDsStrip,\n  body.gmv-is-viewer #gmvCategoriesSyncRowDetails,\n  body.gmv-is-viewer #gmvClientsSyncRowDetails { display: none !important; }\n</style>\n</head>",
        "css rule"
    )
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] CSS belt-and-braces applied.")

if __name__ == '__main__':
    main()
