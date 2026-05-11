# -*- coding: utf-8 -*-
"""
Polish the Paliers tab so it speaks the same visual language as the
redesigned scoreboard.

  1. Add a portfolio-overview hero at the top (Roue-style orange band)
     with the seller's stats: clients, gifts open, total GMV — same
     metrics the scoreboard reports, so the two pages are coherent.
  2. Polish the search bar: bigger, with an inline search icon, full-
     width, paired with the Save button on a separate row.
  3. Section headers stay but get tightened typography and a subtle hover.
  4. Add a small "next prize" preview in the collapsed card summary so
     sellers see WHAT they're working towards without expanding.
"""
import io, sys

P = '/sessions/vibrant-tender-mayer/mnt/Rehab app ( planner) - Copie/rigab_app/index.html'
src = io.open(P, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'

def go(s, old, new, label):
    o = old.replace('\n', nl); n = new.replace('\n', nl)
    if n in s and o not in s: print('  [skip] ' + label); return s
    if o not in s: print('  [FAIL] ' + label); sys.exit(2)
    if s.count(o) != 1: print('  [FAIL] ' + label + ' (count ' + str(s.count(o)) + ')'); sys.exit(2)
    print('  [ok]   ' + label); return s.replace(o, n, 1)

def strip_block(s, begin, end):
    if begin not in s or end not in s: return s
    a = s.index(begin); b = s.index(end) + len(end)
    e = b
    while e < len(s) and s[e] in ('\n', '\r'): e += 1
    st = a
    while st > 0 and s[st-1] in ('\n', '\r'): st -= 1
    return s[:st] + s[e:]


# ---- 1) CSS: polish search bar + add 'next prize' chip styles ---------
CSS_BEGIN = '/* === PALIERS POLISH — polish_paliers_page.py === */'
CSS_END   = '/* === END PALIERS POLISH === */'
src = strip_block(src, CSS_BEGIN, CSS_END)

CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  .pal-searchbar {\n'
    '    position: relative; flex: 1; min-width: 200px;\n'
    '  }\n'
    '  .pal-searchbar svg {\n'
    '    position: absolute; left: 12px; top: 50%; transform: translateY(-50%);\n'
    '    width: 16px; height: 16px; color: #94a3b8; pointer-events: none;\n'
    '  }\n'
    '  [dir="rtl"] .pal-searchbar svg { left: auto; right: 12px; }\n'
    '  .pal-searchbar input {\n'
    '    width: 100%; height: 40px; padding: 0 14px 0 38px;\n'
    '    border: 1px solid #e5e7eb; border-radius: 10px;\n'
    '    font-size: 13.5px; background: #fff;\n'
    '    transition: border-color .12s, box-shadow .12s;\n'
    '    box-sizing: border-box;\n'
    '  }\n'
    '  [dir="rtl"] .pal-searchbar input { padding: 0 38px 0 14px; }\n'
    '  .pal-searchbar input:hover  { border-color: #cbd5e1; }\n'
    '  .pal-searchbar input:focus  { outline: 0; border-color: var(--rf-orange, #f6624a); box-shadow: 0 0 0 3px rgba(246, 98, 74, .12); }\n'
    '\n'
    '  .pal-save-btn {\n'
    '    background: #0f172a; color: #fff;\n'
    '    border: 0; padding: 0 18px; height: 40px;\n'
    '    border-radius: 10px;\n'
    '    font-size: 13px; font-weight: 700;\n'
    '    cursor: pointer; flex-shrink: 0;\n'
    '    transition: background .12s, transform .08s;\n'
    '  }\n'
    '  .pal-save-btn:hover  { background: #1e293b; }\n'
    '  .pal-save-btn:active { transform: scale(.97); }\n'
    '\n'
    '  /* Next-prize preview chip on collapsed cards. */\n'
    '  .pcard-summary-prize {\n'
    '    margin-top: 8px;\n'
    '    display: flex; align-items: center; gap: 8px;\n'
    '    padding: 6px 10px;\n'
    '    background: #fff7ed; border: 1px solid #fed7aa;\n'
    '    border-radius: 8px;\n'
    '    font-size: 11.5px; color: #9a3412;\n'
    '  }\n'
    '  .pcard-summary-prize svg { width: 14px; height: 14px; flex-shrink: 0; }\n'
    '  .pcard-summary-prize-name {\n'
    '    flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;\n'
    '    font-weight: 600;\n'
    '  }\n'
    '  .pcard-summary-prize-tag {\n'
    '    font-size: 9px; font-weight: 800; letter-spacing: .08em;\n'
    '    text-transform: uppercase; color: #c2410c;\n'
    '    background: #ffedd5; padding: 2px 6px; border-radius: 99px; flex-shrink: 0;\n'
    '  }\n'
    + CSS_END
)

css_anchor = '/* === END SCOREBOARD REDESIGN === */'
if css_anchor not in src:
    print('  [FAIL] CSS anchor not found'); sys.exit(2)
src = src.replace(css_anchor, css_anchor + nl + '  ' + CSS_BLOCK.replace('\n', nl), 1)
print('  [ok]   injected paliers polish CSS')


# ---- 2) Build a portfolio hero at the top of the paliers panel ---------
# Use the same data the scoreboard uses. Compute it inline.
# Anchor: right before we set panel.innerHTML.
src = go(src,
    "  panel.innerHTML = `\n"
    "    <div style=\"display:flex; gap:8px; align-items:center; margin:0 0 10px; flex-wrap:wrap;\">\n"
    "      <input type=\"search\" id=\"palSearch\" placeholder=\"${engT('pal_search')}\" value=\"${gmvEscapeHtmlEng(_palQ)}\" autocomplete=\"off\" style=\"flex:1; min-width:160px; padding:8px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:13px; background:#fff;\" />\n"
    "      <button type=\"button\" id=\"engSavePaliers\" class=\"btn btn-primary\" style=\"font-size:12px; padding:8px 14px; background:#0f172a; color:#fff; border:0; border-radius:8px; font-weight:600; cursor:pointer; flex-shrink:0;\">${engT('eng_save')}</button>\n"
    "    </div>\n",
    "  // Portfolio hero — same metrics as the scoreboard so the two pages\n"
    "  // tell a consistent story.\n"
    "  const _gmvTotal = myPhonesAll.reduce((t, p) => t + ((caM1[p] || 0) + (caM2[p] || 0)), 0);\n"
    "  const _giftsOpen = _counts.won;\n"
    "  const _searchIcon = `<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"11\" cy=\"11\" r=\"7\"/><line x1=\"21\" y1=\"21\" x2=\"16.65\" y2=\"16.65\"/></svg>`;\n"
    "  const _portfolioHero = `\n"
    "    <section class=\"sb-hero\" style=\"margin-bottom:12px;\">\n"
    "      <div class=\"sb-hero-eyebrow\">${engT('pal_portfolio')} · ${period}</div>\n"
    "      <h2 class=\"sb-hero-name\">${gmvEscapeHtmlEng(seller)}</h2>\n"
    "      <div class=\"sb-hero-stats\">\n"
    "        <div class=\"sb-hero-stat\"><b>${myPhonesAll.length}</b><span>${engT('sb_stat_clients')}</span></div>\n"
    "        <div class=\"sb-hero-stat\"><b>${_giftsOpen}</b><span>${engT('sb_stat_gifts')}</span></div>\n"
    "        <div class=\"sb-hero-stat\"><b>${fmt(_gmvTotal)}</b><span>MAD · ${engT('sb_stat_gmv')}</span></div>\n"
    "      </div>\n"
    "    </section>`;\n"
    "  panel.innerHTML = `\n"
    "    ${_portfolioHero}\n"
    "    <div style=\"display:flex; gap:10px; align-items:center; margin:0 0 12px; flex-wrap:wrap;\">\n"
    "      <div class=\"pal-searchbar\">\n"
    "        ${_searchIcon}\n"
    "        <input type=\"search\" id=\"palSearch\" placeholder=\"${engT('pal_search')}\" value=\"${gmvEscapeHtmlEng(_palQ)}\" autocomplete=\"off\" />\n"
    "      </div>\n"
    "      <button type=\"button\" id=\"engSavePaliers\" class=\"pal-save-btn\">${engT('eng_save')}</button>\n"
    "    </div>\n",
    'add portfolio hero + polished search bar')


# ---- 3) Add a "next prize" chip in each card's collapsed summary -------
src = go(src,
    "    const _summaryProg = targetP ? Math.min(100, Math.round((cBoth / (targetP.threshold || 1)) * 100)) : (allDone ? 100 : 0);\n"
    "    const _summaryLabel = allDone\n"
    "      ? engT('pal_all_done')\n"
    "      : (targetP ? engT('pal_lvl', { n: targetP.palier }) : '');\n"
    "    const _summaryMeta = (targetP && !allDone)\n"
    "      ? `<span><b>${fmt(cBoth)}</b> / ${fmt(targetP.threshold)} MAD</span>`\n"
    "      : '';\n",
    "    const _summaryProg = targetP ? Math.min(100, Math.round((cBoth / (targetP.threshold || 1)) * 100)) : (allDone ? 100 : 0);\n"
    "    const _summaryLabel = allDone\n"
    "      ? engT('pal_all_done')\n"
    "      : (targetP ? engT('pal_lvl', { n: targetP.palier }) : '');\n"
    "    const _summaryMeta = (targetP && !allDone)\n"
    "      ? `<span><b>${fmt(cBoth)}</b> / ${fmt(targetP.threshold)} MAD</span>`\n"
    "      : '';\n"
    "    // First non-empty prize at the next-target palier — shown as a\n"
    "    // small orange chip so sellers know what they're playing for.\n"
    "    const _nextPrize = targetP ? (targetP.prize1 || targetP.prize2 || targetP.prize3 || '') : '';\n"
    "    const _giftIcon  = '<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><polyline points=\"20 12 20 22 4 22 4 12\"/><rect x=\"2\" y=\"7\" width=\"20\" height=\"5\"/><line x1=\"12\" y1=\"22\" x2=\"12\" y2=\"7\"/><path d=\"M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z\"/><path d=\"M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z\"/></svg>';\n"
    "    const _nextPrizeHtml = (_nextPrize && !allDone)\n"
    "      ? `<div class=\"pcard-summary-prize\">${_giftIcon}<span class=\"pcard-summary-prize-name\" title=\"${gmvEscapeHtmlEng(_nextPrize)}\">${gmvEscapeHtmlEng(_nextPrize)}</span><span class=\"pcard-summary-prize-tag\">${engT('pal_prize_at')} P${targetP.palier}</span></div>`\n"
    "      : '';\n",
    'compute next-prize preview chip')

# Insert _nextPrizeHtml below the summary chips.
src = go(src,
    "          <div class=\"pcard-summary-chips\">\n"
    "            <span class=\"pcard-summary-chip${prodOk ? ' is-open' : ''}\">${prodOk ? '✓' : '•'} ${engT('pal_my_products')} ${myProds.length}/${ENG_CLIENT_MIN_PRODUCTS}</span>\n"
    "            <span class=\"pcard-summary-chip${m1Open ? ' is-open' : ''}\">${m1Open ? '✓' : '🔒'} ${engT('pal_may_gift')}</span>\n"
    "            <span class=\"pcard-summary-chip${bothOpen ? ' is-open' : ''}\">${bothOpen ? '✓' : '🔒'} ${engT('pal_both_gift')}</span>\n"
    "          </div>\n"
    "        </div>\n",
    "          <div class=\"pcard-summary-chips\">\n"
    "            <span class=\"pcard-summary-chip${prodOk ? ' is-open' : ''}\">${prodOk ? '✓' : '•'} ${engT('pal_my_products')} ${myProds.length}/${ENG_CLIENT_MIN_PRODUCTS}</span>\n"
    "            <span class=\"pcard-summary-chip${m1Open ? ' is-open' : ''}\">${m1Open ? '✓' : '🔒'} ${engT('pal_may_gift')}</span>\n"
    "            <span class=\"pcard-summary-chip${bothOpen ? ' is-open' : ''}\">${bothOpen ? '✓' : '🔒'} ${engT('pal_both_gift')}</span>\n"
    "          </div>\n"
    "          ${_nextPrizeHtml}\n"
    "        </div>\n",
    'inject next-prize chip into card summary')


# ---- 4) i18n keys ------------------------------------------------------
def add_after(s, anchor, addition, label):
    o = anchor.replace('\n', nl)
    n = o + addition.replace('\n', nl)
    if n in s and o not in s: print('  [skip] ' + label); return s
    if o not in s: print('  [FAIL] ' + label); sys.exit(2)
    if s.count(o) != 1: print('  [FAIL] ' + label + ' (count ' + str(s.count(o)) + ')'); sys.exit(2)
    print('  [ok]   ' + label)
    return s.replace(o, n, 1)

src = add_after(src,
    "    sb_status_title: 'Statut de mon portefeuille',\n",
    "    pal_portfolio: 'Mon portefeuille', pal_prize_at: 'au',\n",
    'FR pal_portfolio / pal_prize_at')

src = add_after(src,
    "    sb_status_title: 'My portfolio status',\n",
    "    pal_portfolio: 'My portfolio', pal_prize_at: 'at',\n",
    'EN pal_portfolio / pal_prize_at')

src = add_after(src,
    "    sb_status_title: 'حالة محفظتي',\n",
    "    pal_portfolio: 'محفظتي', pal_prize_at: 'في',\n",
    'AR pal_portfolio / pal_prize_at')


io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
