#!/usr/bin/env python3
"""Align bullet-chart scale labels with the actual tick position (75% mark)."""
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
    if "transform:translateX(-50%)" in src:
        print("[skip] already aligned"); return

    old = (
        "        '<div class=\"hero-bullet-scale\">' +\n"
        "          '<span>0</span>' +\n"
        "          '<span title=\"Target ' + gmvFmtFull(totalTarget) + ' MAD\">target</span>' +\n"
        "          '<span>' + gmvFmtCompact(scaleMax) + ' MAD</span>' +\n"
        "        '</div>';"
    )
    new = (
        "        '<div class=\"hero-bullet-scale\" style=\"position:relative; height:14px;\">' +\n"
        "          '<span style=\"position:absolute; left:0;\">0</span>' +\n"
        "          '<span title=\"Target ' + gmvFmtFull(totalTarget) + ' MAD\" style=\"position:absolute; left:75%; transform:translateX(-50%); white-space:nowrap;\">target ' + gmvFmtCompact(totalTarget) + '</span>' +\n"
        "          '<span style=\"position:absolute; right:0;\">' + gmvFmtCompact(scaleMax) + ' MAD</span>' +\n"
        "        '</div>';"
    )
    src = must_replace_once(src, old, new, "bullet labels")
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] bullet labels now align with the tick.")

if __name__ == '__main__':
    main()
