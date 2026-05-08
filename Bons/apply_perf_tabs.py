#!/usr/bin/env python3
"""Add By Seller / By Store / By Category tabs to the GMV Performance page."""
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
    if "data-perf-view" in src:
        print("[skip] already done"); return

    old = (
        "  if (window.__gmvByStoreFragment) html += window.__gmvByStoreFragment;\n"
        "  if (window.__gmvByCategoryFragment) html += window.__gmvByCategoryFragment;\n"
        "\n"
        "  wrap.innerHTML = html;"
    )
    new = (
        "  if (page === 'performance') {\n"
        "    if (!gmv.perfView) {\n"
        "      try { gmv.perfView = loadJSON('rihab_gmv_perfview_v1') || 'seller'; } catch (_) { gmv.perfView = 'seller'; }\n"
        "    }\n"
        "    const view = gmv.perfView;\n"
        "    const tabBtn = (id, label) => '<button type=\"button\" data-perf-view=\"' + id + '\" style=\"padding:8px 16px; border-radius:8px; border:1px solid var(--border); background:' + (view===id?'var(--accent, #0f172a)':'transparent') + '; color:' + (view===id?'#fff':'inherit') + '; font-weight:600; cursor:pointer; font-size:13px;\">' + label + '</button>';\n"
        "    const tabs = '<div style=\"display:flex; gap:8px; margin:0 0 16px; flex-wrap:wrap;\">' + tabBtn('seller','By Seller') + tabBtn('store','By Store') + tabBtn('category','By Category') + '</div>';\n"
        "    const sec = (id, body) => '<div data-perf-sec=\"' + id + '\"' + (view===id?'':' style=\"display:none;\"') + '>' + body + '</div>';\n"
        "    const sellerBody = html;\n"
        "    const storeBody  = window.__gmvByStoreFragment    || '<div class=\"gmv-empty\">No store data \\u2014 upload orders with storeName.</div>';\n"
        "    const catBody    = window.__gmvByCategoryFragment || '<div class=\"gmv-empty\">No category data \\u2014 upload product categories file.</div>';\n"
        "    wrap.innerHTML = tabs + sec('seller', sellerBody) + sec('store', storeBody) + sec('category', catBody);\n"
        "    wrap.querySelectorAll('button[data-perf-view]').forEach(btn => {\n"
        "      btn.addEventListener('click', () => {\n"
        "        gmv.perfView = btn.dataset.perfView;\n"
        "        try { saveJSON('rihab_gmv_perfview_v1', gmv.perfView); } catch (_) {}\n"
        "        gmvRenderResults();\n"
        "      });\n"
        "    });\n"
        "  } else {\n"
        "    if (window.__gmvByStoreFragment) html += window.__gmvByStoreFragment;\n"
        "    if (window.__gmvByCategoryFragment) html += window.__gmvByCategoryFragment;\n"
        "    wrap.innerHTML = html;\n"
        "  }"
    )
    src = must_replace_once(src, old, new, "perf tabs")
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] Performance page now has By Seller / By Store / By Category tabs.")

if __name__ == '__main__':
    main()
