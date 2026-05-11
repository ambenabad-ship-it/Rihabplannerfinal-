# -*- coding: utf-8 -*-
"""
Re-apply the progressive paliers JS changes.
The first attempt bailed before writing because it also tried to insert
i18n keys that fix_paliers_i18n.py had already added. This version only
does the JS edits.
"""
import io, sys

P = '/sessions/vibrant-tender-mayer/mnt/Rehab app ( planner) - Copie/rigab_app/index.html'
src = io.open(P, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'

def go(s, old, new, label):
    o = old.replace('\n', nl); n = new.replace('\n', nl)
    if n in s and o not in s:
        print('  [skip] ' + label); return s
    if o not in s:
        print('  [FAIL] ' + label); sys.exit(2)
    if s.count(o) != 1:
        print('  [FAIL] ' + label + ' (count ' + str(s.count(o)) + ')'); sys.exit(2)
    print('  [ok]   ' + label); return s.replace(o, n, 1)

# 1) Per-card render: drop manual target dropdown, auto-progress.
src = go(src,
    "  myPhones.forEach(phone => {\n"
    "    const cl       = (gmv.clients || {})[phone] || {};\n"
    "    const target   = palTgts[phone] || 0;\n"
    "    const targetP  = (gmvEngagement.paliers || []).find(p => p.palier === parseInt(target));\n"
    "    const cM1      = caM1[phone] || 0;\n"
    "    const cBoth    = (caM1[phone] || 0) + (caM2[phone] || 0);\n"
    "    const ach      = gmvAchievedPalier(cBoth);\n",
    "  // Sort paliers ascending so the auto-progression has stable ordering.\n"
    "  const sortedPaliers = (gmvEngagement.paliers || []).slice().sort((a, b) => (a.palier || 0) - (b.palier || 0));\n"
    "  myPhones.forEach(phone => {\n"
    "    const cl       = (gmv.clients || {})[phone] || {};\n"
    "    const cM1      = caM1[phone] || 0;\n"
    "    const cBoth    = (caM1[phone] || 0) + (caM2[phone] || 0);\n"
    "    // Highest palier already crossed by cumulative May+June GMV.\n"
    "    const ach      = gmvAchievedPalier(cBoth);\n"
    "    // Next-target palier = first palier whose threshold is still ahead.\n"
    "    // Defaults to Palier 1 when nothing has been crossed yet.\n"
    "    const targetP  = sortedPaliers.find(p => (p.threshold || 0) > cBoth) || null;\n"
    "    const allDone  = !targetP && sortedPaliers.length > 0;\n",
    'auto-target palier (replaces dropdown logic)')

# 2) Replace the dropdown row with the next-target summary.
src = go(src,
    "        <div style=\"margin-top:12px; padding-top:10px; border-top:1px solid #f1f5f9; display:flex; align-items:center; gap:10px; font-size:12px;\">\n"
    "          <span style=\"color:#64748b; flex-shrink:0;\">${engT('pal_target')} :</span>\n"
    "          <select data-eng-palier=\"${gmvEscapeHtmlEng(phone)}\" style=\"flex:1; padding:6px 8px; border:1px solid #cbd5e1; border-radius:6px; font-size:12px; background:#fff;\">\n"
    "            ${palierOpts.replace('value=\"' + target + '\"', 'value=\"' + target + '\" selected')}\n"
    "          </select>\n"
    "        </div>\n",
    "        ${(() => {\n"
    "          if (allDone) {\n"
    "            return `<div style=\"margin-top:12px; padding:10px 12px; border-radius:8px; background:#f0fdf4; border:1px solid #86efac; font-size:12px; color:#15803d; font-weight:600; text-align:center;\">${engT('pal_all_done')}</div>`;\n"
    "          }\n"
    "          if (!targetP) return '';\n"
    "          const remaining = Math.max(0, (targetP.threshold || 0) - cBoth);\n"
    "          const progPct = Math.min(100, Math.round((cBoth / (targetP.threshold || 1)) * 100));\n"
    "          return `<div style=\"margin-top:12px; padding-top:10px; border-top:1px solid #f1f5f9;\">\n"
    "            <div style=\"display:flex; justify-content:space-between; align-items:baseline; font-size:12px; gap:8px; flex-wrap:wrap;\">\n"
    "              <span style=\"color:#64748b;\">${engT('pal_next_target')} : <b style=\"color:#0f172a;\">${engT('pal_lvl', { n: targetP.palier })}</b></span>\n"
    "              <span style=\"color:#64748b; font-size:11px;\"><b style=\"color:#0f172a;\">${fmt(cBoth)}</b> / ${fmt(targetP.threshold)} MAD</span>\n"
    "            </div>\n"
    "            <div style=\"height:5px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:6px;\">\n"
    "              <div style=\"height:100%; width:${progPct}%; background:#3b82f6; transition:width .4s;\"></div>\n"
    "            </div>\n"
    "            <div style=\"font-size:11px; color:#64748b; margin-top:5px;\">${engT('pal_remaining', { n: fmt(remaining) })}</div>\n"
    "          </div>`;\n"
    "        })()}\n",
    'replace dropdown with auto next-target summary')

# 3) Save handler: drop palier targets collection.
src = go(src,
    "  if (saveBtn) saveBtn.addEventListener('click', async () => {\n"
    "    const paliers = {};\n"
    "    panel.querySelectorAll('[data-eng-palier]').forEach(s => {\n"
    "      const v = parseInt(s.value); if (v > 0) paliers[s.dataset.engPalier] = v;\n"
    "    });\n"
    "    const cFocusOut = {};\n"
    "    panel.querySelectorAll('[data-pal-prod]:checked').forEach(cb => {\n"
    "      const phone = cb.dataset.palProd;\n"
    "      const code  = cb.value;\n"
    "      if (!cFocusOut[phone]) cFocusOut[phone] = {};\n"
    "      cFocusOut[phone][code] = { selected: true };\n"
    "    });\n"
    "    try {\n"
    "      await gmvSaveEngagementCommitment(seller, period, { paliers, clientFocus: cFocusOut });\n",
    "  if (saveBtn) saveBtn.addEventListener('click', async () => {\n"
    "    // Palier targets are now auto-derived from GMV — only collect\n"
    "    // per-client product commitments from the UI.\n"
    "    const cFocusOut = {};\n"
    "    panel.querySelectorAll('[data-pal-prod]:checked').forEach(cb => {\n"
    "      const phone = cb.dataset.palProd;\n"
    "      const code  = cb.value;\n"
    "      if (!cFocusOut[phone]) cFocusOut[phone] = {};\n"
    "      cFocusOut[phone][code] = { selected: true };\n"
    "    });\n"
    "    try {\n"
    "      await gmvSaveEngagementCommitment(seller, period, { clientFocus: cFocusOut });\n",
    'save handler skips palier targets')

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
