# -*- coding: utf-8 -*-
"""
Collapse the per-client palier cards by default.

Each card now shows just:
  * Header (name, phone, achieved-palier badge, chevron)
  * Inline summary row: next-palier name + progress bar + percentage +
    two milestone status chips (May / May+June)

Tapping the header expands the full hero / commit / milestones panel.
A header toolbar exposes "Expand all" / "Collapse all" controls.

State persists in gmvEngagement.expandedPaliers[phone] across renders so
the user's choice survives search and save.
"""
import io, sys

P = '/sessions/vibrant-tender-mayer/mnt/Rehab app ( planner) - Copie/rigab_app/index.html'
src = io.open(P, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
fails = []

def go(s, old, new, label):
    o = old.replace('\n', nl); n = new.replace('\n', nl)
    if n in s and o not in s: print('  [skip] ' + label); return s
    if o not in s: print('  [FAIL] ' + label); fails.append(label); return s
    if s.count(o) != 1: print('  [FAIL] ' + label + ' (count ' + str(s.count(o)) + ')'); fails.append(label); return s
    print('  [ok]   ' + label)
    return s.replace(o, n, 1)


# ---- 1) Add CSS for collapsed state + summary + chevron ----------------
CSS_BEGIN = '/* === PCARD COLLAPSE/EXPAND — compact_paliers.py === */'
CSS_END   = '/* === END PCARD COLLAPSE/EXPAND === */'

if CSS_BEGIN in src and CSS_END in src:
    a = src.index(CSS_BEGIN); b = src.index(CSS_END) + len(CSS_END)
    e = b
    while e < len(src) and src[e] in ('\n', '\r'): e += 1
    st = a
    while st > 0 and src[st-1] in ('\n', '\r'): st -= 1
    src = src[:st] + src[e:]

CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  .pcard { padding: 0; cursor: default; }\n'
    '  .pcard-head {\n'
    '    margin: 0; padding: 14px 16px;\n'
    '    cursor: pointer; user-select: none;\n'
    '    transition: background .12s;\n'
    '  }\n'
    '  .pcard-head:hover { background: #f9fafb; border-radius: 16px 16px 0 0; }\n'
    '  .pcard:not(.pcard--open) .pcard-head:hover { border-radius: 16px; }\n'
    '  .pcard-head-right {\n'
    '    display: flex; align-items: center; gap: 8px; flex-shrink: 0;\n'
    '  }\n'
    '  .pcard-chevron {\n'
    '    width: 24px; height: 24px; border-radius: 50%;\n'
    '    background: #f1f5f9; color: #475569;\n'
    '    display: inline-flex; align-items: center; justify-content: center;\n'
    '    font-size: 11px; flex-shrink: 0;\n'
    '    transition: transform .2s, background .12s;\n'
    '  }\n'
    '  .pcard--open .pcard-chevron { transform: rotate(180deg); background: #e2e8f0; }\n'
    '\n'
    '  /* Collapsed summary row beneath the head, visible only when closed. */\n'
    '  .pcard-summary {\n'
    '    padding: 0 16px 14px;\n'
    '    display: block;\n'
    '  }\n'
    '  .pcard--open .pcard-summary { display: none; }\n'
    '  .pcard-summary-line {\n'
    '    display: flex; align-items: baseline; gap: 8px; justify-content: space-between;\n'
    '    font-size: 12px; color: #475569;\n'
    '    margin-bottom: 6px; flex-wrap: wrap;\n'
    '  }\n'
    '  .pcard-summary-line b { color: #0f172a; font-weight: 700; font-variant-numeric: tabular-nums; }\n'
    '  .pcard-summary-pct {\n'
    '    font-weight: 800; font-variant-numeric: tabular-nums;\n'
    '    color: var(--rf-orange-dark, #d54b33);\n'
    '  }\n'
    '  .pcard-summary-pct.is-done { color: #15803d; }\n'
    '  .pcard-summary-bar {\n'
    '    height: 5px; background: #f1f5f9;\n'
    '    border-radius: 99px; overflow: hidden; margin-bottom: 10px;\n'
    '  }\n'
    '  .pcard-summary-bar > span {\n'
    '    display: block; height: 100%;\n'
    '    background: linear-gradient(90deg, var(--rf-orange, #f6624a), var(--rf-orange-dark, #d54b33));\n'
    '    border-radius: 99px;\n'
    '    transition: width .6s cubic-bezier(.2,.7,.3,1);\n'
    '  }\n'
    '  .pcard-summary-bar.is-done > span { background: linear-gradient(90deg, #22c55e, #16a34a); }\n'
    '  .pcard-summary-chips { display: flex; gap: 6px; flex-wrap: wrap; }\n'
    '  .pcard-summary-chip {\n'
    '    font-size: 10.5px; font-weight: 700;\n'
    '    padding: 4px 10px; border-radius: 99px;\n'
    '    background: #f1f5f9; color: #6b7280;\n'
    '    display: inline-flex; align-items: center; gap: 5px;\n'
    '    border: 1px solid #e5e7eb;\n'
    '  }\n'
    '  .pcard-summary-chip.is-open { background: #dcfce7; color: #15803d; border-color: #86efac; }\n'
    '\n'
    '  /* Expanded panel: holds the hero, commit, milestones. */\n'
    '  .pcard-body {\n'
    '    padding: 0 16px 16px;\n'
    '    display: block;\n'
    '    border-top: 1px solid #f1f5f9;\n'
    '    padding-top: 14px;\n'
    '  }\n'
    '  .pcard:not(.pcard--open) .pcard-body { display: none; }\n'
    '\n'
    '  /* Tighten the bulk paddings/margins inside the expanded panel. */\n'
    '  .pcard-body .pcard-hero { margin-bottom: 12px; }\n'
    '  .pcard-body .pcard-commit { margin-bottom: 12px; }\n'
    '  .pcard-body .pcard-milestone + .pcard-milestone { margin-top: 6px; }\n'
    '\n'
    '  /* Header toolbar: expand-all / collapse-all controls. */\n'
    '  .pal-toolbar {\n'
    '    display: flex; gap: 6px; align-items: center;\n'
    '    margin: 0 0 10px;\n'
    '  }\n'
    '  .pal-toolbar-btn {\n'
    '    background: #fff; border: 1px solid #e5e7eb;\n'
    '    color: #475569;\n'
    '    padding: 6px 10px; border-radius: 8px;\n'
    '    font-size: 11px; font-weight: 600;\n'
    '    cursor: pointer; line-height: 1.3;\n'
    '  }\n'
    '  .pal-toolbar-btn:hover { background: #f9fafb; color: #0f172a; }\n'
    '\n'
    '  /* Optional desktop 2-column grid for very wide screens. */\n'
    '  @media (min-width: 900px) {\n'
    '    .pal-cards-grid {\n'
    '      display: grid;\n'
    '      grid-template-columns: 1fr 1fr;\n'
    '      gap: 12px;\n'
    '    }\n'
    '    .pal-cards-grid > .pcard { margin-bottom: 0; }\n'
    '  }\n'
    + CSS_END
)

css_anchor = '/* === END PALIER CARD PREMIUM REDESIGN === */'
if css_anchor not in src:
    print('  [FAIL] CSS anchor not found'); sys.exit(2)
src = src.replace(css_anchor, css_anchor + nl + '  ' + CSS_BLOCK.replace('\n', nl), 1)
print('  [ok]   injected pcard collapse CSS')


# ---- 2) Add expand state to engagement state object --------------------
src = go(src,
    "  activeSubtab: 'paliers',\n",
    "  activeSubtab: 'paliers',\n"
    "  expandedPaliers: {},  // phone -> true when a client's card is expanded\n",
    'state: expandedPaliers map')


# ---- 3) Rewrite the per-card HTML to split into head/summary/body ------
src = go(src,
    "    cardsHtml += `\n"
    "      <article class=\"pcard\">\n"
    "        <header class=\"pcard-head\">\n"
    "          <div style=\"min-width:0; flex:1;\">\n"
    "            <div class=\"pcard-name\">${gmvEscapeHtmlEng(cl.name || '(no name)')}</div>\n"
    "            <div class=\"pcard-phone\">${gmvEscapeHtmlEng(phone)}</div>\n"
    "          </div>\n"
    "          ${ach ? `<span class=\"pcard-badge\">${engT('pal_achieved')} ${ach.palier}</span>` : ''}\n"
    "        </header>\n"
    "        ${_heroBlock}\n"
    "        <section class=\"pcard-commit\">\n",
    "    const _open = !!(gmvEngagement.expandedPaliers && gmvEngagement.expandedPaliers[phone]);\n"
    "    const _summaryProg = targetP ? Math.min(100, Math.round((cBoth / (targetP.threshold || 1)) * 100)) : (allDone ? 100 : 0);\n"
    "    const _summaryLabel = allDone\n"
    "      ? engT('pal_all_done')\n"
    "      : (targetP ? engT('pal_lvl', { n: targetP.palier }) : '');\n"
    "    const _summaryMeta = (targetP && !allDone)\n"
    "      ? `<span><b>${fmt(cBoth)}</b> / ${fmt(targetP.threshold)} MAD</span>`\n"
    "      : '';\n"
    "    cardsHtml += `\n"
    "      <article class=\"pcard${_open ? ' pcard--open' : ''}\">\n"
    "        <header class=\"pcard-head\" data-pal-toggle=\"${gmvEscapeHtmlEng(phone)}\">\n"
    "          <div style=\"min-width:0; flex:1;\">\n"
    "            <div class=\"pcard-name\">${gmvEscapeHtmlEng(cl.name || '(no name)')}</div>\n"
    "            <div class=\"pcard-phone\">${gmvEscapeHtmlEng(phone)}</div>\n"
    "          </div>\n"
    "          <div class=\"pcard-head-right\">\n"
    "            ${ach ? `<span class=\"pcard-badge\">${engT('pal_achieved')} ${ach.palier}</span>` : ''}\n"
    "            <span class=\"pcard-chevron\" aria-hidden=\"true\">▾</span>\n"
    "          </div>\n"
    "        </header>\n"
    "        <div class=\"pcard-summary\">\n"
    "          ${_summaryLabel ? `<div class=\"pcard-summary-line\">\n"
    "            <span style=\"color:#64748b;\">${engT('pal_next_target')} : <b style=\"color:#0f172a;\">${_summaryLabel}</b></span>\n"
    "            ${_summaryMeta}\n"
    "            <span class=\"pcard-summary-pct${allDone ? ' is-done' : ''}\">${_summaryProg}%</span>\n"
    "          </div>` : ''}\n"
    "          <div class=\"pcard-summary-bar${allDone ? ' is-done' : ''}\"><span style=\"width:${_summaryProg}%\"></span></div>\n"
    "          <div class=\"pcard-summary-chips\">\n"
    "            <span class=\"pcard-summary-chip${prodOk ? ' is-open' : ''}\">${prodOk ? '✓' : '•'} ${engT('pal_my_products')} ${myProds.length}/${ENG_CLIENT_MIN_PRODUCTS}</span>\n"
    "            <span class=\"pcard-summary-chip${m1Open ? ' is-open' : ''}\">${m1Open ? '✓' : '🔒'} ${engT('pal_may_gift')}</span>\n"
    "            <span class=\"pcard-summary-chip${bothOpen ? ' is-open' : ''}\">${bothOpen ? '✓' : '🔒'} ${engT('pal_both_gift')}</span>\n"
    "          </div>\n"
    "        </div>\n"
    "        <div class=\"pcard-body\">\n"
    "        ${_heroBlock}\n"
    "        <section class=\"pcard-commit\">\n",
    'card head/summary/body split + collapsed-by-default')


# ---- 4) Close pcard-body wrapper at the card tail ---------------------
src = go(src,
    "        <section class=\"pcard-milestones\">\n"
    "          <div class=\"pcard-milestones-label\">${engT('pal_milestones')}</div>\n"
    "          ${_milestone(m1Open,   m1Count,   ENG_CLIENT_MILESTONE_M1,   engT('pal_may_gift'),  cM1,   targetP ? targetP.threshold : 0)}\n"
    "          ${_milestone(bothOpen, bothCount, ENG_CLIENT_MILESTONE_BOTH, engT('pal_both_gift'), cBoth, targetP ? targetP.threshold : 0)}\n"
    "        </section>\n"
    "      </article>`;\n",
    "        <section class=\"pcard-milestones\">\n"
    "          <div class=\"pcard-milestones-label\">${engT('pal_milestones')}</div>\n"
    "          ${_milestone(m1Open,   m1Count,   ENG_CLIENT_MILESTONE_M1,   engT('pal_may_gift'),  cM1,   targetP ? targetP.threshold : 0)}\n"
    "          ${_milestone(bothOpen, bothCount, ENG_CLIENT_MILESTONE_BOTH, engT('pal_both_gift'), cBoth, targetP ? targetP.threshold : 0)}\n"
    "        </section>\n"
    "        </div>\n"
    "      </article>`;\n",
    'close pcard-body div')


# ---- 5) Wrap the cardsHtml grid + add toolbar ---------------------
src = go(src,
    "  panel.innerHTML = `\n"
    "    <div style=\"display:flex; gap:8px; align-items:center; margin:0 0 10px; flex-wrap:wrap;\">\n"
    "      <input type=\"search\" id=\"palSearch\" placeholder=\"${engT('pal_search')}\" value=\"${gmvEscapeHtmlEng(_palQ)}\" autocomplete=\"off\" style=\"flex:1; min-width:160px; padding:8px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:13px; background:#fff;\" />\n"
    "      <button type=\"button\" id=\"engSavePaliers\" class=\"btn btn-primary\" style=\"font-size:12px; padding:8px 14px; background:#0f172a; color:#fff; border:0; border-radius:8px; font-weight:600; cursor:pointer; flex-shrink:0;\">${engT('eng_save')}</button>\n"
    "    </div>\n"
    "    <div style=\"font-size:12px; color:#64748b; margin:0 0 10px;\">${_countTxt}</div>\n"
    "    ${cardsHtml}`;\n",
    "  panel.innerHTML = `\n"
    "    <div style=\"display:flex; gap:8px; align-items:center; margin:0 0 10px; flex-wrap:wrap;\">\n"
    "      <input type=\"search\" id=\"palSearch\" placeholder=\"${engT('pal_search')}\" value=\"${gmvEscapeHtmlEng(_palQ)}\" autocomplete=\"off\" style=\"flex:1; min-width:160px; padding:8px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:13px; background:#fff;\" />\n"
    "      <button type=\"button\" id=\"engSavePaliers\" class=\"btn btn-primary\" style=\"font-size:12px; padding:8px 14px; background:#0f172a; color:#fff; border:0; border-radius:8px; font-weight:600; cursor:pointer; flex-shrink:0;\">${engT('eng_save')}</button>\n"
    "    </div>\n"
    "    <div class=\"pal-toolbar\">\n"
    "      <div style=\"font-size:12px; color:#64748b; flex:1;\">${_countTxt}</div>\n"
    "      <button type=\"button\" id=\"palExpandAll\"   class=\"pal-toolbar-btn\">${engT('pal_expand_all')}</button>\n"
    "      <button type=\"button\" id=\"palCollapseAll\" class=\"pal-toolbar-btn\">${engT('pal_collapse_all')}</button>\n"
    "    </div>\n"
    "    <div class=\"pal-cards-grid\">${cardsHtml}</div>`;\n",
    'toolbar with expand-all / collapse-all + grid wrap')


# ---- 6) Wire toggle handler + expand/collapse all ---------------------
src = go(src,
    "  // Wire expand toggles for the per-client product list.\n",
    "  // Wire the head-tap toggle that opens/closes a client card.\n"
    "  panel.querySelectorAll('[data-pal-toggle]').forEach(h => {\n"
    "    h.addEventListener('click', () => {\n"
    "      const phone = h.dataset.palToggle;\n"
    "      const card = h.closest('.pcard');\n"
    "      if (!card) return;\n"
    "      const open = card.classList.toggle('pcard--open');\n"
    "      if (!gmvEngagement.expandedPaliers) gmvEngagement.expandedPaliers = {};\n"
    "      if (open) gmvEngagement.expandedPaliers[phone] = true;\n"
    "      else      delete gmvEngagement.expandedPaliers[phone];\n"
    "    });\n"
    "  });\n"
    "  const _expAll = document.getElementById('palExpandAll');\n"
    "  if (_expAll) _expAll.addEventListener('click', () => {\n"
    "    if (!gmvEngagement.expandedPaliers) gmvEngagement.expandedPaliers = {};\n"
    "    myPhonesAll.forEach(p => { gmvEngagement.expandedPaliers[p] = true; });\n"
    "    gmvRenderEngagementPaliers(panel, mySeller, isCreator);\n"
    "  });\n"
    "  const _colAll = document.getElementById('palCollapseAll');\n"
    "  if (_colAll) _colAll.addEventListener('click', () => {\n"
    "    gmvEngagement.expandedPaliers = {};\n"
    "    gmvRenderEngagementPaliers(panel, mySeller, isCreator);\n"
    "  });\n"
    "  // Wire expand toggles for the per-client product list.\n",
    'toggle handler + expand-all / collapse-all wiring')


# ---- 7) Add i18n keys ------------------------------------------------
src = go(src,
    "    pal_milestones: 'Jalons de la campagne',\n",
    "    pal_milestones: 'Jalons de la campagne',\n"
    "    pal_expand_all: 'Tout déplier', pal_collapse_all: 'Tout replier',\n",
    'FR pal_expand_all/pal_collapse_all')

src = go(src,
    "    pal_milestones: 'Campaign milestones',\n",
    "    pal_milestones: 'Campaign milestones',\n"
    "    pal_expand_all: 'Expand all', pal_collapse_all: 'Collapse all',\n",
    'EN pal_expand_all/pal_collapse_all')

src = go(src,
    "    pal_milestones: 'مراحل الحملة',\n",
    "    pal_milestones: 'مراحل الحملة',\n"
    "    pal_expand_all: 'فتح الكل', pal_collapse_all: 'إغلاق الكل',\n",
    'AR pal_expand_all/pal_collapse_all')


if fails:
    print('FAIL — not writing. ' + str(len(fails)) + ' step(s) failed.')
    sys.exit(2)

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
