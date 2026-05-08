#!/usr/bin/env python3
"""Fix: gmvApplyRoleUI() wasn't running after sign-in for non-creators."""
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
    if "gmvApplyRoleUI" not in src:
        sys.exit("[FAIL] phase 1 patch isn't applied yet")

    n = 0

    # 1) Run on post-sign-in
    old_signin = (
        "          if (typeof gmvRefreshSyncBtn === 'function') gmvRefreshSyncBtn();\n"
        "          if (typeof gmvRenderAll === 'function') gmvRenderAll();"
    )
    new_signin = (
        "          if (typeof gmvRefreshSyncBtn === 'function') gmvRefreshSyncBtn();\n"
        "          if (typeof gmvApplyRoleUI === 'function') gmvApplyRoleUI();\n"
        "          if (typeof gmvRenderAll === 'function') gmvRenderAll();"
    )
    if old_signin in src and new_signin not in src:
        src = src.replace(old_signin, new_signin, 1); n += 1; print("[OK] post-sign-in hook")

    # 2) Belt & braces: run on every gmvRenderAll too
    old_renderall = "function gmvRenderAll() {"
    if old_renderall in src and "gmvApplyRoleUI();" not in src.split(old_renderall)[1].split("}")[0]:
        new_renderall = "function gmvRenderAll() {\n  try { gmvApplyRoleUI(); } catch (_) {}"
        src = must_replace_once(src, old_renderall, new_renderall, "gmvRenderAll prefix")
        n += 1; print("[OK] gmvRenderAll hook")

    if n == 0:
        print("[skip] both hooks already in place"); return
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("\nDone. Hard-refresh and sign in as the viewer — strip should hide.")

if __name__ == '__main__':
    main()
