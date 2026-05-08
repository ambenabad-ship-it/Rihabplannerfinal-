#!/usr/bin/env python3
"""Drop the confusing scale-max label so target+scale-max no longer overlap."""
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
        "        '<div class=\"hero-bullet-scale\" style=\"position:relative; height:14px;\">' +\n"
        "          '<span style=\"position:absolute; left:0;\">0</span>' +\n"
        "          '<span title=\"Target ' + gmvFmtFull(totalTarget) + ' MAD\" style=\"position:absolute; left:75%; transform:translateX(-50%); white-space:nowrap;\">target ' + gmvFmtCompact(totalTarget) + '</span>' +\n"
        "          '<span style=\"position:absolute; right:0;\">' + gmvFmtCompact(scaleMax) + ' MAD</span>' +\n"
        "        '</div>';"
    )
    new = (
        "        '<div class=\"hero-bullet-scale\" style=\"position:relative; height:14px;\">' +\n"
        "          '<span style=\"position:absolute; left:0;\">0</span>' +\n"
        "          '<span title=\"Target ' + gmvFmtFull(totalTarget) + ' MAD\" style=\"position:absolute; left:75%; transform:translateX(-50%); white-space:nowrap;\">target ' + gmvFmtCompact(totalTarget) + ' MAD</span>' +\n"
        "        '</div>';"
    )
    if new in src:
        print("[skip] already done"); return
    src = must_replace_once(src, old, new, "drop scale max")
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] only 0 and target labels remain.")

if __name__ == '__main__':
    main()
