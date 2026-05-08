#!/usr/bin/env python3
"""Bullet bars: target = right edge of bar, no tick. Applied everywhere."""
import os, sys
TARGET = r"C:\Users\KamalSAGUEM\OneDrive - Beyond believers\Bureau\Rehab app ( planner) - Copie\rigab_app\index.html"

def main():
    with open(TARGET, 'r', encoding='utf-8') as f:
        src = f.read()
    original = src
    n = 0

    # 1) Hero bullet
    old1 = (
        "      const scaleMax = totalTarget / 0.75;\n"
        "      const fillPct = Math.max(0, Math.min(100, (total / scaleMax) * 100));\n"
        "      const tickPct = 75;\n"
        "      const ok = total >= totalTarget;\n"
        "      bulletEl.innerHTML =\n"
        "        '<div class=\"hero-bullet-bar\">' +\n"
        "          '<div class=\"hero-bullet-fill\" style=\"width:' + fillPct + '%; background:' + (ok ? 'linear-gradient(90deg,var(--success) 0%,#10b981 100%)' : 'linear-gradient(90deg,var(--primary) 0%,var(--primary-600) 100%)') + ';\"></div>' +\n"
        "          '<div class=\"hero-bullet-tick\" style=\"left:' + tickPct + '%;\"></div>' +\n"
        "        '</div>' +\n"
        "        '<div class=\"hero-bullet-scale\" style=\"position:relative; height:14px;\">' +\n"
        "          '<span style=\"position:absolute; left:0;\">0</span>' +\n"
        "          '<span title=\"Target ' + gmvFmtFull(totalTarget) + ' MAD\" style=\"position:absolute; left:75%; transform:translateX(-50%); white-space:nowrap;\">target ' + gmvFmtCompact(totalTarget) + ' MAD</span>' +\n"
        "        '</div>';"
    )
    new1 = (
        "      const fillPct = Math.max(0, Math.min(100, (total / totalTarget) * 100));\n"
        "      const ok = total >= totalTarget;\n"
        "      bulletEl.innerHTML =\n"
        "        '<div class=\"hero-bullet-bar\">' +\n"
        "          '<div class=\"hero-bullet-fill\" style=\"width:' + fillPct + '%; background:' + (ok ? 'linear-gradient(90deg,var(--success) 0%,#10b981 100%)' : 'linear-gradient(90deg,var(--primary) 0%,var(--primary-600) 100%)') + ';\"></div>' +\n"
        "        '</div>' +\n"
        "        '<div class=\"hero-bullet-scale\" style=\"display:flex; justify-content:space-between;\">' +\n"
        "          '<span>0</span>' +\n"
        "          '<span title=\"Target ' + gmvFmtFull(totalTarget) + ' MAD\">target ' + gmvFmtCompact(totalTarget) + ' MAD</span>' +\n"
        "        '</div>';"
    )
    if old1 in src:
        src = src.replace(old1, new1, 1); n += 1; print("[OK] hero bullet")
    else:
        print("[skip] hero bullet")

    # 2) Inline bullet helper in gmvRenderResults
    old2 = (
        "    if (!(target > 0)) return '<span style=\"font-size:11px; color:var(--text-soft);\">0</span>';\n"
        "    // Same trick as the hero bullet — target locked at 75% mark.\n"
        "    const scaleMax = target / 0.75;\n"
        "    const fillPct = Math.max(0, Math.min(100, (reached / scaleMax) * 100));\n"
        "    const tickPct = 75;\n"
        "    const ok = reached >= target;\n"
        "    return '<div class=\"gmv-bullet\" title=\"' + gmvFmtFull(reached) + ' / ' + gmvFmtFull(target) + ' MAD\">' +\n"
        "      '<div class=\"gmv-bullet-fill ' + (ok ? 'ok' : 'partial') + '\" style=\"width:' + fillPct + '%;\"></div>' +\n"
        "      '<div class=\"gmv-bullet-tick\" style=\"left:' + tickPct + '%;\"></div>' +\n"
        "    '</div>';"
    )
    new2 = (
        "    if (!(target > 0)) return '<span style=\"font-size:11px; color:var(--text-soft);\">0</span>';\n"
        "    const fillPct = Math.max(0, Math.min(100, (reached / target) * 100));\n"
        "    const ok = reached >= target;\n"
        "    return '<div class=\"gmv-bullet\" title=\"' + gmvFmtFull(reached) + ' / ' + gmvFmtFull(target) + ' MAD\">' +\n"
        "      '<div class=\"gmv-bullet-fill ' + (ok ? 'ok' : 'partial') + '\" style=\"width:' + fillPct + '%;\"></div>' +\n"
        "    '</div>';"
    )
    if old2 in src:
        src = src.replace(old2, new2, 1); n += 1; print("[OK] inline bullet helper")
    else:
        print("[skip] inline bullet")

    # 3) byStore per-row bullet
    old3 = (
        "          const scaleMax = storeT / 0.75;\n"
        "          const fillPct = Math.max(0, Math.min(100, (delivered / scaleMax) * 100));\n"
        "          const tickPct = 75;\n"
        "          const ok = delivered >= storeT;\n"
        "          bulletHtml = '<div class=\"gmv-bullet\" title=\"' + gmvFmtFull(delivered) + ' / ' + gmvFmtFull(storeT) + ' MAD\">' +\n"
        "            '<div class=\"gmv-bullet-fill ' + (ok ? 'ok' : 'partial') + '\" style=\"width:' + fillPct + '%;\"></div>' +\n"
        "            '<div class=\"gmv-bullet-tick\" style=\"left:' + tickPct + '%;\"></div>' +\n"
        "          '</div>';"
    )
    new3 = (
        "          const fillPct = Math.max(0, Math.min(100, (delivered / storeT) * 100));\n"
        "          const ok = delivered >= storeT;\n"
        "          bulletHtml = '<div class=\"gmv-bullet\" title=\"' + gmvFmtFull(delivered) + ' / ' + gmvFmtFull(storeT) + ' MAD\">' +\n"
        "            '<div class=\"gmv-bullet-fill ' + (ok ? 'ok' : 'partial') + '\" style=\"width:' + fillPct + '%;\"></div>' +\n"
        "          '</div>';"
    )
    if old3 in src:
        src = src.replace(old3, new3, 1); n += 1; print("[OK] byStore row bullet")
    else:
        print("[skip] byStore row bullet")

    # 4) byStore grand total bullet
    old4 = (
        "        const scaleMax = _allStoresT / 0.75;\n"
        "        const fillPct = Math.max(0, Math.min(100, (_totalDelivered / scaleMax) * 100));\n"
        "        const ok = _totalDelivered >= _allStoresT;\n"
        "        _totalBullet = '<div class=\"gmv-bullet\" title=\"' + gmvFmtFull(_totalDelivered) + ' / ' + gmvFmtFull(_allStoresT) + ' MAD\">' +\n"
        "          '<div class=\"gmv-bullet-fill ' + (ok ? 'ok' : 'partial') + '\" style=\"width:' + fillPct + '%;\"></div>' +\n"
        "          '<div class=\"gmv-bullet-tick\" style=\"left:75%;\"></div>' +\n"
        "        '</div>';"
    )
    new4 = (
        "        const fillPct = Math.max(0, Math.min(100, (_totalDelivered / _allStoresT) * 100));\n"
        "        const ok = _totalDelivered >= _allStoresT;\n"
        "        _totalBullet = '<div class=\"gmv-bullet\" title=\"' + gmvFmtFull(_totalDelivered) + ' / ' + gmvFmtFull(_allStoresT) + ' MAD\">' +\n"
        "          '<div class=\"gmv-bullet-fill ' + (ok ? 'ok' : 'partial') + '\" style=\"width:' + fillPct + '%;\"></div>' +\n"
        "        '</div>';"
    )
    if old4 in src:
        src = src.replace(old4, new4, 1); n += 1; print("[OK] byStore grand total bullet")
    else:
        print("[skip] byStore grand total")

    # 5) Flat performance bullet (added in earlier patch)
    old5 = (
        "      const scaleMax = target / 0.75;\n"
        "      const fillPct = Math.max(0, Math.min(100, (delivered / scaleMax) * 100));\n"
        "      const ok = delivered >= target;\n"
        "      bulletHtml = '<div class=\"gmv-bullet\" title=\"' + gmvFmtFull(delivered) + ' / ' + gmvFmtFull(target) + ' MAD\"><div class=\"gmv-bullet-fill ' + (ok ? 'ok' : 'partial') + '\" style=\"width:' + fillPct + '%;\"></div><div class=\"gmv-bullet-tick\" style=\"left:75%;\"></div></div>';"
    )
    new5 = (
        "      const fillPct = Math.max(0, Math.min(100, (delivered / target) * 100));\n"
        "      const ok = delivered >= target;\n"
        "      bulletHtml = '<div class=\"gmv-bullet\" title=\"' + gmvFmtFull(delivered) + ' / ' + gmvFmtFull(target) + ' MAD\"><div class=\"gmv-bullet-fill ' + (ok ? 'ok' : 'partial') + '\" style=\"width:' + fillPct + '%;\"></div></div>';"
    )
    if old5 in src:
        src = src.replace(old5, new5, 1); n += 1; print("[OK] flat performance bullet")
    else:
        print("[skip] flat perf bullet")

    if src == original:
        print("\nNothing to change."); return
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("\nDone (" + str(n) + " bullet sites updated). Hard-refresh.")

if __name__ == '__main__':
    main()
