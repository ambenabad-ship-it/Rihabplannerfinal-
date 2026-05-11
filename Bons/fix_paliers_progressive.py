# -*- coding: utf-8 -*-
"""
Paliers — progressive unlock.

Replace the manual "target palier" dropdown with automatic progression:
  * Every client starts at palier 1 by default.
  * As a client's cumulative May+June GMV crosses each palier threshold,
    the next palier becomes the "current target" automatically.
  * The May gift / May+June gift status checks against the auto-target
    so sellers see exactly what they're aiming at next.
  * Saving no longer collects palier targets from the UI (auto-derived).
"""
import io, sys

INDEX_PATH = '/sessions/vibrant-tender-mayer/mnt/Rehab app ( planner) - Copie/rigab_app/index.html'
src = io.open(INDEX_PATH, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'

def replace_once(s, old, new, label):
    o = old.replace('\n', nl)
    n = new.replace('\n', nl)
    if n in s and o not in s:
        print('  [skip] ' + label); return s
    if o not in s:
        print('  [FAIL] ' + label + ' (anchor not found)'); sys.exit(2)
    if s.count(o) != 1:
        print('  [FAIL] ' + label + ' (anchor not unique: ' + str(s.count(o)) + ')'); sys.exit(2)
    print('  [ok]   ' + label)
    return s.replace(o, n, 1)


# ---- 1) Replace the per-card render block: target dropdown -> auto-progress
OLD_RENDER = (
    "  myPhones.forEach(phone => {\n"
    "    const cl       = (gmv.clients || {})[phone] || {};\n"
    "    const target   = palTgts[phone] || 0;\n"
    "    const targetP  = (gmvEngagement.paliers || []).find(p => p.palier === parseInt(target));\n"
    "    const cM1      = caM1[phone] || 0;\n"
    "    const cBoth    = (caM1[phone] || 0) + (caM2[phone] || 0);\n"
    "    const ach      = gmvAchievedPalier(cBoth);\n"
)

NEW_RENDER = (
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
    "    const allDone  = !targetP && sortedPaliers.length > 0;\n"
)
src = replace_once(src, OLD_RENDER, NEW_RENDER, 'auto-target palier (replaces dropdown logic)')


# ---- 2) Replace the dropdown row with a 'next target' summary
OLD_DROPDOWN = (
    "        <div style=\"margin-top:12px; padding-top:10px; border-top:1px solid #f1f5f9; display:flex; align-items:center; gap:10px; font-size:12px;\">\n"
    "          <span style=\"color:#64748b; flex-shrink:0;\">${engT('pal_target')} :</span>\n"
    "          <select data-eng-palier=\"${gmvEscapeHtmlEng(phone)}\" style=\"flex:1; padding:6px 8px; border:1px solid #cbd5e1; border-radius:6px; font-size:12px; background:#fff;\">\n"
    "            ${palierOpts.replace('value=\"' + target + '\"', 'value=\"' + target + '\" selected')}\n"
    "          </select>\n"
    "        </div>\n"
)

NEW_DROPDOWN = (
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
    "        })()}\n"
)
src = replace_once(src, OLD_DROPDOWN, NEW_DROPDOWN, 'replace dropdown with auto next-target summary')


# ---- 3) Save handler no longer collects palier targets from UI.
OLD_SAVE_BLOCK = (
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
    "      await gmvSaveEngagementCommitment(seller, period, { paliers, clientFocus: cFocusOut });\n"
)

NEW_SAVE_BLOCK = (
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
    "      await gmvSaveEngagementCommitment(seller, period, { clientFocus: cFocusOut });\n"
)
src = replace_once(src, OLD_SAVE_BLOCK, NEW_SAVE_BLOCK, 'save handler skips palier targets')


# ---- 4) Add the new i18n keys (FR/EN/AR) -------------------------------
src = replace_once(src,
    "    pal_my_products: 'Mes produits engagés',\n",
    "    pal_my_products: 'Mes produits engagés',\n"
    "    pal_next_target: 'Prochain palier', pal_remaining: '{n} MAD restants pour le débloquer',\n"
    "    pal_all_done: '🎉 Tous les paliers atteints !',\n",
    'i18n FR: pal_next_target / pal_remaining / pal_all_done')

src = replace_once(src,
    "    pal_my_products: 'My committed products',\n",
    "    pal_my_products: 'My committed products',\n"
    "    pal_next_target: 'Next palier', pal_remaining: '{n} MAD to go to unlock it',\n"
    "    pal_all_done: '🎉 All paliers achieved!',\n",
    'i18n EN: pal_next_target / pal_remaining / pal_all_done')

src = replace_once(src,
    "    pal_my_products: 'منتجاتي الملتزم بها',\n",
    "    pal_my_products: 'منتجاتي الملتزم بها',\n"
    "    pal_next_target: 'المستوى التالي', pal_remaining: 'متبقي {n} درهم لفتحه',\n"
    "    pal_all_done: '🎉 تم بلوغ كل المستويات !',\n",
    'i18n AR: pal_next_target / pal_remaining / pal_all_done')


io.open(INDEX_PATH, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
