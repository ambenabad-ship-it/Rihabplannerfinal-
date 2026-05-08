#!/usr/bin/env python3
"""Fix-up: adds the missing 3rd upload tile (Categories) to the GMV Tracker UI."""
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

    if 'id="gmvCategoriesFile"' in src:
        print("[skip] tile already in DOM — nothing to do.")
        return

    # 1) ds-strip pill
    src = must_replace_once(
        src,
        '        <span class="ds-pill" id="gmvDsOrdersPill">\n          <span class="ds-check">○</span>\n          <span>Orders</span>\n          <span class="ds-count" id="gmvDsOrdersCount">not loaded</span>\n        </span>',
        '        <span class="ds-pill" id="gmvDsOrdersPill">\n          <span class="ds-check">○</span>\n          <span>Orders</span>\n          <span class="ds-count" id="gmvDsOrdersCount">not loaded</span>\n        </span>\n        <span class="ds-pill" id="gmvDsCategoriesPill">\n          <span class="ds-check">○</span>\n          <span>Categories</span>\n          <span class="ds-count" id="gmvDsCategoriesCount">not loaded</span>\n        </span>',
        "L1: pill"
    )

    # 2) ds-card (insert AFTER orders card, BEFORE the closing </div></details> of the body)
    new_card = (
        '        <div class="gmv-ds-card">\n'
        '          <div class="ds-card-title">3 · Product Categories</div>\n'
        '          <label class="file-drop">\n'
        '            <div class="file-drop-icon">\n'
        '              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>\n'
        '            </div>\n'
        '            <div class="file-drop-text">\n'
        '              <div class="file-drop-title">Drop product categories file</div>\n'
        '              <div class="file-drop-hint">code · description · category (columns: Code / Description / Category)</div>\n'
        '            </div>\n'
        '            <input type="file" id="gmvCategoriesFile" accept=".xlsx,.xls,.csv">\n'
        '          </label>\n'
        '          <div id="gmvCategoriesSummary" class="gmv-summary" style="display:none;"></div>\n'
        '        </div>\n'
    )
    src = must_replace_once(
        src,
        '          <div id="gmvOrdersSummary" class="gmv-summary" style="display:none;"></div>\n        </div>\n      </div>\n    </details>',
        '          <div id="gmvOrdersSummary" class="gmv-summary" style="display:none;"></div>\n        </div>\n' + new_card + '      </div>\n    </details>',
        "L2: card"
    )

    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] tile added. Hard-refresh the app (Ctrl+Shift+R).")

if __name__ == '__main__':
    main()
