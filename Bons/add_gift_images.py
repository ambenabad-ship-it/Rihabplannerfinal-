# -*- coding: utf-8 -*-
"""
Wire gift thumbnail images through the paliers pipeline.

1. Upload parser learns Image 1 / Image 2 / Image 3 columns and stores
   them as image1/image2/image3 on each palier object.
2. The per-client palier card's "next target" hero medals show a small
   square thumbnail when an image is present (falls back to the numbered
   medal disc otherwise).
3. The collapsed card's "next prize" chip also previews the thumbnail.
4. CSS adds .pcard-prize-img + .pcard-summary-prize-img classes.
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


# ---- 1) Update parser to read Image 1/2/3 columns ---------------------
src = go(src,
    "  const c1 = findCol(rows[0], ['Prize 1','prize 1','prize1','Cadeau 1','cadeau1']);\n"
    "  const c2 = findCol(rows[0], ['Prize 2','prize 2','prize2','Cadeau 2','cadeau2']);\n"
    "  const c3 = findCol(rows[0], ['Prize 3','prize 3','prize3','Cadeau 3','cadeau3']);\n"
    "  if (!cP || !cT) throw new Error('Need Palier + Threshold columns.');\n"
    "  const out = [];\n"
    "  rows.forEach(r => {\n"
    "    const p = parseInt(r[cP]) || 0;\n"
    "    if (!p) return;\n"
    "    out.push({\n"
    "      palier: p,\n"
    "      threshold: parseFloat(r[cT]) || 0,\n"
    "      prize1: c1 ? String(r[c1] || '').trim() : '',\n"
    "      prize2: c2 ? String(r[c2] || '').trim() : '',\n"
    "      prize3: c3 ? String(r[c3] || '').trim() : '',\n"
    "    });\n"
    "  });\n",
    "  const c1 = findCol(rows[0], ['Prize 1','prize 1','prize1','Cadeau 1','cadeau1']);\n"
    "  const c2 = findCol(rows[0], ['Prize 2','prize 2','prize2','Cadeau 2','cadeau2']);\n"
    "  const c3 = findCol(rows[0], ['Prize 3','prize 3','prize3','Cadeau 3','cadeau3']);\n"
    "  const cI1 = findCol(rows[0], ['Image 1','image 1','image1','Img 1','img1','Photo 1','photo1']);\n"
    "  const cI2 = findCol(rows[0], ['Image 2','image 2','image2','Img 2','img2','Photo 2','photo2']);\n"
    "  const cI3 = findCol(rows[0], ['Image 3','image 3','image3','Img 3','img3','Photo 3','photo3']);\n"
    "  if (!cP || !cT) throw new Error('Need Palier + Threshold columns.');\n"
    "  const out = [];\n"
    "  rows.forEach(r => {\n"
    "    const p = parseInt(r[cP]) || 0;\n"
    "    if (!p) return;\n"
    "    out.push({\n"
    "      palier: p,\n"
    "      threshold: parseFloat(r[cT]) || 0,\n"
    "      prize1: c1 ? String(r[c1] || '').trim() : '',\n"
    "      prize2: c2 ? String(r[c2] || '').trim() : '',\n"
    "      prize3: c3 ? String(r[c3] || '').trim() : '',\n"
    "      image1: cI1 ? String(r[cI1] || '').trim() : '',\n"
    "      image2: cI2 ? String(r[cI2] || '').trim() : '',\n"
    "      image3: cI3 ? String(r[cI3] || '').trim() : '',\n"
    "    });\n"
    "  });\n",
    'parser reads Image 1/2/3 columns')


# ---- 2) CSS for image thumbnails --------------------------------------
CSS_BEGIN = '/* === GIFT IMAGES — add_gift_images.py === */'
CSS_END   = '/* === END GIFT IMAGES === */'
# Strip existing block to allow re-runs.
if CSS_BEGIN in src and CSS_END in src:
    a = src.index(CSS_BEGIN); b = src.index(CSS_END) + len(CSS_END)
    e = b
    while e < len(src) and src[e] in ('\n', '\r'): e += 1
    st = a
    while st > 0 and src[st-1] in ('\n', '\r'): st -= 1
    src = src[:st] + src[e:]

CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  /* Image thumb inside a prize row in the hero. */\n'
    '  .pcard-prize-img {\n'
    '    width: 44px; height: 44px; border-radius: 8px;\n'
    '    object-fit: cover; flex-shrink: 0;\n'
    '    background: #f8fafc; border: 1px solid #e5e7eb;\n'
    '    padding: 2px; box-sizing: border-box;\n'
    '  }\n'
    '  .pcard-prize-1.has-img { padding-left: 8px; }\n'
    '  .pcard-prize-1.has-img .pcard-prize-img { box-shadow: inset 0 0 0 2px var(--rf-bronze, #b57032); }\n'
    '  .pcard-prize-2.has-img .pcard-prize-img { box-shadow: inset 0 0 0 2px var(--rf-silver, #6b7b8c); }\n'
    '  .pcard-prize-3.has-img .pcard-prize-img { box-shadow: inset 0 0 0 2px var(--rf-gold, #c9a227); }\n'
    '\n'
    '  /* Image thumb inside the collapsed-card next-prize chip. */\n'
    '  .pcard-summary-prize-img {\n'
    '    width: 26px; height: 26px; border-radius: 6px;\n'
    '    object-fit: cover; flex-shrink: 0;\n'
    '    background: #fff; border: 1px solid #fed7aa;\n'
    '    padding: 1px; box-sizing: border-box;\n'
    '  }\n'
    + CSS_END
)

css_anchor = '/* === END EXPLICIT UNLOCK RULE === */'
if css_anchor not in src:
    print('  [FAIL] CSS anchor not found'); sys.exit(2)
src = src.replace(css_anchor, css_anchor + nl + '  ' + CSS_BLOCK.replace('\n', nl), 1)
print('  [ok]   injected gift-image CSS')


# ---- 3) Render image in the prize medal rows (next-target hero) -------
src = go(src,
    "      const _prizes = [\n"
    "        { tag: engT('rf_medal_1'), prize: targetP.prize1 || '' },\n"
    "        { tag: engT('rf_medal_2'), prize: targetP.prize2 || '' },\n"
    "        { tag: engT('rf_medal_3'), prize: targetP.prize3 || '' },\n"
    "      ].filter(m => m.prize);\n"
    "      const _prizesHtml = _prizes.length\n"
    "        ? `<div class=\"pcard-prizes\">\n"
    "             <div class=\"pcard-prizes-label\">🎁 ${engT('rf_prizes')}</div>\n"
    "             <div class=\"pcard-prize-list\">\n"
    "               ${_prizes.map((m, i) => `<div class=\"pcard-prize pcard-prize-${i + 1}\">\n"
    "                 <span class=\"pcard-prize-medal\">${i + 1}</span>\n"
    "                 <span class=\"pcard-prize-name\" title=\"${gmvEscapeHtmlEng(m.prize)}\">${gmvEscapeHtmlEng(m.prize)}</span>\n"
    "                 <span class=\"pcard-prize-tag\">${m.tag}</span>\n"
    "               </div>`).join('')}\n"
    "             </div>\n"
    "           </div>`\n"
    "        : '';\n",
    "      const _prizes = [\n"
    "        { tag: engT('rf_medal_1'), prize: targetP.prize1 || '', image: targetP.image1 || '' },\n"
    "        { tag: engT('rf_medal_2'), prize: targetP.prize2 || '', image: targetP.image2 || '' },\n"
    "        { tag: engT('rf_medal_3'), prize: targetP.prize3 || '', image: targetP.image3 || '' },\n"
    "      ].filter(m => m.prize);\n"
    "      const _prizesHtml = _prizes.length\n"
    "        ? `<div class=\"pcard-prizes\">\n"
    "             <div class=\"pcard-prizes-label\">🎁 ${engT('rf_prizes')}</div>\n"
    "             <div class=\"pcard-prize-list\">\n"
    "               ${_prizes.map((m, i) => {\n"
    "                 const hasImg = !!m.image;\n"
    "                 const lead = hasImg\n"
    "                   ? `<img class=\"pcard-prize-img\" src=\"${m.image}\" alt=\"\" loading=\"lazy\">`\n"
    "                   : `<span class=\"pcard-prize-medal\">${i + 1}</span>`;\n"
    "                 return `<div class=\"pcard-prize pcard-prize-${i + 1}${hasImg ? ' has-img' : ''}\">\n"
    "                   ${lead}\n"
    "                   <span class=\"pcard-prize-name\" title=\"${gmvEscapeHtmlEng(m.prize)}\">${gmvEscapeHtmlEng(m.prize)}</span>\n"
    "                   <span class=\"pcard-prize-tag\">${m.tag}</span>\n"
    "                 </div>`;\n"
    "               }).join('')}\n"
    "             </div>\n"
    "           </div>`\n"
    "        : '';\n",
    'next-target hero prize rows: image thumb')


# ---- 4) Render image in the collapsed-card next-prize chip ------------
src = go(src,
    "    // First non-empty prize at the next-target palier — shown as a\n"
    "    // small orange chip so sellers know what they're playing for.\n"
    "    const _nextPrize = targetP ? (targetP.prize1 || targetP.prize2 || targetP.prize3 || '') : '';\n"
    "    const _giftIcon  = '<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><polyline points=\"20 12 20 22 4 22 4 12\"/><rect x=\"2\" y=\"7\" width=\"20\" height=\"5\"/><line x1=\"12\" y1=\"22\" x2=\"12\" y2=\"7\"/><path d=\"M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z\"/><path d=\"M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z\"/></svg>';\n"
    "    const _nextPrizeHtml = (_nextPrize && !allDone)\n"
    "      ? `<div class=\"pcard-summary-prize\">${_giftIcon}<span class=\"pcard-summary-prize-name\" title=\"${gmvEscapeHtmlEng(_nextPrize)}\">${gmvEscapeHtmlEng(_nextPrize)}</span><span class=\"pcard-summary-prize-tag\">${engT('pal_prize_at')} P${targetP.palier}</span></div>`\n"
    "      : '';\n",
    "    // First non-empty prize at the next-target palier — shown as a\n"
    "    // small orange chip so sellers know what they're playing for.\n"
    "    const _nextPrize = targetP ? (targetP.prize1 || targetP.prize2 || targetP.prize3 || '') : '';\n"
    "    const _nextPrizeImg = targetP ? (targetP.image1 || targetP.image2 || targetP.image3 || '') : '';\n"
    "    const _giftIcon  = '<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><polyline points=\"20 12 20 22 4 22 4 12\"/><rect x=\"2\" y=\"7\" width=\"20\" height=\"5\"/><line x1=\"12\" y1=\"22\" x2=\"12\" y2=\"7\"/><path d=\"M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z\"/><path d=\"M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z\"/></svg>';\n"
    "    const _nextPrizeLead = _nextPrizeImg\n"
    "      ? `<img class=\"pcard-summary-prize-img\" src=\"${_nextPrizeImg}\" alt=\"\" loading=\"lazy\">`\n"
    "      : _giftIcon;\n"
    "    const _nextPrizeHtml = (_nextPrize && !allDone)\n"
    "      ? `<div class=\"pcard-summary-prize\">${_nextPrizeLead}<span class=\"pcard-summary-prize-name\" title=\"${gmvEscapeHtmlEng(_nextPrize)}\">${gmvEscapeHtmlEng(_nextPrize)}</span><span class=\"pcard-summary-prize-tag\">${engT('pal_prize_at')} P${targetP.palier}</span></div>`\n"
    "      : '';\n",
    'collapsed-card next-prize chip: image thumb')


if fails:
    print('FAIL — not writing. ' + str(len(fails)) + ' step(s) failed.')
    sys.exit(2)

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
