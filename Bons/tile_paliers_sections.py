# -*- coding: utf-8 -*-
"""
Group the seller paliers cards into 3 collapsible sections by status:

  1. 🎁 Opened palier  — m1Open OR bothOpen (gift unlocked).
  2. ✓ Reached minimum — committed at least ENG_CLIENT_MIN_PRODUCTS
     focus products for the client, no gift yet.
  3. ⏳ Not active yet  — fewer than the minimum committed.

Search still filters across all sections. Each section's expand state
is persisted in gmvEngagement.expandedSections[id].
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


# ---- 1) CSS for the section pills + group container ----------------
CSS_BEGIN = '/* === PALIER SECTIONS — tile_paliers_sections.py === */'
CSS_END   = '/* === END PALIER SECTIONS === */'
if CSS_BEGIN in src and CSS_END in src:
    a = src.index(CSS_BEGIN); b = src.index(CSS_END) + len(CSS_END)
    e = b
    while e < len(src) and src[e] in ('\n', '\r'): e += 1
    st = a
    while st > 0 and src[st-1] in ('\n', '\r'): st -= 1
    src = src[:st] + src[e:]

CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  .pal-section {\n'
    '    margin-bottom: 18px;\n'
    '  }\n'
    '  .pal-section-head {\n'
    '    display: flex; align-items: center; gap: 10px;\n'
    '    padding: 12px 14px; cursor: pointer; user-select: none;\n'
    '    background: #fff;\n'
    '    border: 1px solid #e5e7eb; border-radius: 12px;\n'
    '    transition: background .12s, border-color .12s;\n'
    '  }\n'
    '  .pal-section-head:hover { background: #f9fafb; border-color: #d1d5db; }\n'
    '  .pal-section--open .pal-section-head { border-radius: 12px 12px 0 0; border-bottom-color: transparent; }\n'
    '  .pal-section-icon {\n'
    '    width: 32px; height: 32px; border-radius: 50%;\n'
    '    display: inline-flex; align-items: center; justify-content: center;\n'
    '    font-size: 16px; flex-shrink: 0;\n'
    '  }\n'
    '  .pal-section--won .pal-section-icon  { background: #fff7ed; color: #c2410c; box-shadow: inset 0 0 0 1px #fed7aa; }\n'
    '  .pal-section--ok .pal-section-icon   { background: #f0fdf4; color: #15803d; box-shadow: inset 0 0 0 1px #86efac; }\n'
    '  .pal-section--idle .pal-section-icon { background: #f1f5f9; color: #64748b; box-shadow: inset 0 0 0 1px #cbd5e1; }\n'
    '  .pal-section-title {\n'
    '    flex: 1; min-width: 0;\n'
    '    font-size: 14px; font-weight: 700; color: #0f172a; line-height: 1.2;\n'
    '  }\n'
    '  .pal-section-sub {\n'
    '    font-size: 11px; color: #64748b; margin-top: 2px; font-weight: 500;\n'
    '  }\n'
    '  .pal-section-count {\n'
    '    background: #f1f5f9; color: #475569;\n'
    '    padding: 3px 10px; border-radius: 99px;\n'
    '    font-size: 11.5px; font-weight: 800;\n'
    '    font-variant-numeric: tabular-nums; flex-shrink: 0;\n'
    '  }\n'
    '  .pal-section--won .pal-section-count  { background: #fff7ed; color: #c2410c; }\n'
    '  .pal-section--ok .pal-section-count   { background: #f0fdf4; color: #15803d; }\n'
    '  .pal-section--idle .pal-section-count { background: #f1f5f9; color: #475569; }\n'
    '  .pal-section-chev {\n'
    '    width: 20px; height: 20px; flex-shrink: 0; color: #94a3b8;\n'
    '    transition: transform .2s;\n'
    '  }\n'
    '  .pal-section--open .pal-section-chev { transform: rotate(180deg); color: #0f172a; }\n'
    '  .pal-section-body {\n'
    '    border: 1px solid #e5e7eb; border-top: 0;\n'
    '    border-radius: 0 0 12px 12px;\n'
    '    padding: 12px;\n'
    '    background: #fafafa;\n'
    '  }\n'
    '  .pal-section:not(.pal-section--open) .pal-section-body { display: none; }\n'
    '  .pal-section-body .pcard { background: #fff; }\n'
    '  .pal-section-body .pal-cards-grid > .pcard { margin-bottom: 0; }\n'
    '  .pal-section-empty {\n'
    '    padding: 16px; text-align: center; color: #94a3b8; font-size: 12px;\n'
    '    background: #fff; border-radius: 8px; border: 1px dashed #e5e7eb;\n'
    '  }\n'
    + CSS_END
)

css_anchor = '/* === END PCARD COLLAPSE/EXPAND === */'
if css_anchor not in src:
    print('  [FAIL] CSS anchor not found'); sys.exit(2)
src = src.replace(css_anchor, css_anchor + nl + '  ' + CSS_BLOCK.replace('\n', nl), 1)
print('  [ok]   injected section CSS')


# ---- 2) Add expandedSections to engagement state -----------------------
src = go(src,
    "  expandedPaliers: {},  // phone -> true when a client's card is expanded\n",
    "  expandedPaliers: {},  // phone -> true when a client's card is expanded\n"
    "  expandedSections: { won: true, ok: true, idle: false },\n",
    'state: expandedSections')


# ---- 3) Convert the loop to bucket cards into 3 sections ---------------
# Replace `let cardsHtml = '';` and the final `panel.innerHTML = ` block.
src = go(src,
    "  let cardsHtml = '';\n"
    "  // Sort paliers ascending so the auto-progression has stable ordering.\n",
    "  // Three buckets: clients with an unlocked gift, those at minimum\n"
    "  // products, and those who haven't engaged yet.\n"
    "  const _bucket = { won: '', ok: '', idle: '' };\n"
    "  const _counts = { won: 0, ok: 0, idle: 0 };\n"
    "  let cardsHtml = '';\n"
    "  // Sort paliers ascending so the auto-progression has stable ordering.\n",
    'declare buckets next to cardsHtml')


# Append to the right bucket inside the forEach loop. We replace the final
# `cardsHtml += \`` -> a small wrapper that picks the bucket per phone.
src = go(src,
    "    const _open = !!(gmvEngagement.expandedPaliers && gmvEngagement.expandedPaliers[phone]);\n"
    "    const _summaryProg = targetP ? Math.min(100, Math.round((cBoth / (targetP.threshold || 1)) * 100)) : (allDone ? 100 : 0);\n",
    "    // Classify into a bucket BEFORE building the HTML, so we can route it.\n"
    "    const _bucketKey = (m1Open || bothOpen)\n"
    "      ? 'won'\n"
    "      : (prodOk ? 'ok' : 'idle');\n"
    "    _counts[_bucketKey]++;\n"
    "    const _open = !!(gmvEngagement.expandedPaliers && gmvEngagement.expandedPaliers[phone]);\n"
    "    const _summaryProg = targetP ? Math.min(100, Math.round((cBoth / (targetP.threshold || 1)) * 100)) : (allDone ? 100 : 0);\n",
    'classify each card into a bucket')


# Route `cardsHtml += ` to `_bucket[_bucketKey] += `.
src = go(src,
    "    cardsHtml += `\n"
    "      <article class=\"pcard${_open ? ' pcard--open' : ''}\">\n",
    "    _bucket[_bucketKey] += `\n"
    "      <article class=\"pcard${_open ? ' pcard--open' : ''}\">\n",
    'route card append to its bucket')


# ---- 4) Compose the sections HTML and replace the outer wrap ----------
src = go(src,
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
    "  // Build the 3 sections.\n"
    "  const _exp = gmvEngagement.expandedSections || { won: true, ok: true, idle: false };\n"
    "  const _emptyHtml = engT('pal_section_empty');\n"
    "  const _section = (key, title, sub, icon, modCls) => {\n"
    "    const cnt = _counts[key];\n"
    "    const isOpen = !!_exp[key];\n"
    "    return `<section class=\"pal-section ${modCls}${isOpen ? ' pal-section--open' : ''}\">\n"
    "      <header class=\"pal-section-head\" data-pal-section=\"${key}\">\n"
    "        <span class=\"pal-section-icon\">${icon}</span>\n"
    "        <div style=\"flex:1; min-width:0;\">\n"
    "          <div class=\"pal-section-title\">${title}</div>\n"
    "          <div class=\"pal-section-sub\">${sub}</div>\n"
    "        </div>\n"
    "        <span class=\"pal-section-count\">${cnt}</span>\n"
    "        <svg class=\"pal-section-chev\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><polyline points=\"6 9 12 15 18 9\"/></svg>\n"
    "      </header>\n"
    "      <div class=\"pal-section-body\">\n"
    "        ${cnt > 0 ? `<div class=\"pal-cards-grid\">${_bucket[key]}</div>` : `<div class=\"pal-section-empty\">${_emptyHtml}</div>`}\n"
    "      </div>\n"
    "    </section>`;\n"
    "  };\n"
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
    "    ${myPhonesFiltered.length === 0 && _palQ ? cardsHtml : `\n"
    "      ${_section('won',  engT('pal_sec_won_t'),  engT('pal_sec_won_d'),  '🎁', 'pal-section--won')}\n"
    "      ${_section('ok',   engT('pal_sec_ok_t'),   engT('pal_sec_ok_d'),   '✓',  'pal-section--ok')}\n"
    "      ${_section('idle', engT('pal_sec_idle_t'), engT('pal_sec_idle_d'), '⏳', 'pal-section--idle')}\n"
    "    `}`;\n",
    'render 3 sections (won / ok / idle)')


# ---- 5) Wire section toggle handlers + reset expand/collapse all ------
src = go(src,
    "  // Wire the head-tap toggle that opens/closes a client card.\n",
    "  // Wire section-head toggles (open/close a whole status group).\n"
    "  panel.querySelectorAll('[data-pal-section]').forEach(h => {\n"
    "    h.addEventListener('click', () => {\n"
    "      const k = h.dataset.palSection;\n"
    "      if (!gmvEngagement.expandedSections) gmvEngagement.expandedSections = {};\n"
    "      gmvEngagement.expandedSections[k] = !gmvEngagement.expandedSections[k];\n"
    "      const sec = h.closest('.pal-section');\n"
    "      if (sec) sec.classList.toggle('pal-section--open', !!gmvEngagement.expandedSections[k]);\n"
    "    });\n"
    "  });\n"
    "  // Wire the head-tap toggle that opens/closes a client card.\n",
    'wire section-head toggles')


# ---- 6) Add the section i18n keys -----------------------------------
src = go(src,
    "    pal_expand_all: 'Tout déplier', pal_collapse_all: 'Tout replier',\n",
    "    pal_expand_all: 'Tout déplier', pal_collapse_all: 'Tout replier',\n"
    "    pal_sec_won_t: 'Cadeaux débloqués', pal_sec_won_d: 'Au moins un cadeau de palier ouvert.',\n"
    "    pal_sec_ok_t: 'Minimum atteint',     pal_sec_ok_d: '10+ produits engagés, prochain palier en cours.',\n"
    "    pal_sec_idle_t: 'Pas encore actifs', pal_sec_idle_d: 'Moins de 10 produits engagés.',\n"
    "    pal_section_empty: 'Aucun client dans ce groupe pour le moment.',\n",
    'FR section i18n')

src = go(src,
    "    pal_expand_all: 'Expand all', pal_collapse_all: 'Collapse all',\n",
    "    pal_expand_all: 'Expand all', pal_collapse_all: 'Collapse all',\n"
    "    pal_sec_won_t: 'Gifts unlocked',     pal_sec_won_d: 'At least one palier gift opened.',\n"
    "    pal_sec_ok_t: 'Minimum reached',     pal_sec_ok_d: '10+ products committed, working toward next palier.',\n"
    "    pal_sec_idle_t: 'Not active yet',    pal_sec_idle_d: 'Fewer than 10 products committed.',\n"
    "    pal_section_empty: 'No clients in this group yet.',\n",
    'EN section i18n')

src = go(src,
    "    pal_expand_all: 'فتح الكل', pal_collapse_all: 'إغلاق الكل',\n",
    "    pal_expand_all: 'فتح الكل', pal_collapse_all: 'إغلاق الكل',\n"
    "    pal_sec_won_t: 'الهدايا مفتوحة',  pal_sec_won_d: 'هدية مستوى واحدة على الأقل مفتوحة.',\n"
    "    pal_sec_ok_t: 'الحد الأدنى مبلوغ', pal_sec_ok_d: '10+ منتجات ملتزم بها، نحو المستوى التالي.',\n"
    "    pal_sec_idle_t: 'لم ينشط بعد',    pal_sec_idle_d: 'أقل من 10 منتجات ملتزم بها.',\n"
    "    pal_section_empty: 'لا يوجد زبون في هذه الفئة حاليا.',\n",
    'AR section i18n')


if fails:
    print('FAIL — not writing. ' + str(len(fails)) + ' step(s) failed.')
    sys.exit(2)

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
