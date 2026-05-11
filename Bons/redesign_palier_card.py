# -*- coding: utf-8 -*-
"""
Premium redesign of the per-client palier card on the seller view.

  * Card layout reorganised into clear sections with breathing room:
      header → next-palier hero → commitment block → milestones list.
  * New CSS class system .pcard-* (replaces inline-styled card).
  * Prize medals get a proper vertical list inside the hero, each with a
    bronze/silver/gold medal disc + prize name + tier tag.
  * Gift status rows become a clean "milestones" checklist with proper
    open/locked statuses.
  * Mobile-tuned breakpoints.
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


def strip_block(s, begin, end, indent_chars=2):
    if begin not in s or end not in s: return s
    a = s.index(begin); b = s.index(end) + len(end)
    e = b
    while e < len(s) and s[e] in ('\n', '\r'): e += 1
    st = a
    if indent_chars and st >= indent_chars and s[st-indent_chars:st] == ' ' * indent_chars: st -= indent_chars
    while st > 0 and s[st-1] in ('\n', '\r'): st -= 1
    return s[:st] + s[e:]


CSS_BEGIN = '/* === PALIER CARD PREMIUM REDESIGN — redesign_palier_card.py === */'
CSS_END   = '/* === END PALIER CARD PREMIUM REDESIGN === */'
src = strip_block(src, CSS_BEGIN, CSS_END)

CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  .pcard {\n'
    '    background: #fff;\n'
    '    border: 1px solid #e5e7eb;\n'
    '    border-radius: 16px;\n'
    '    padding: 18px;\n'
    '    margin-bottom: 14px;\n'
    '    box-shadow: 0 1px 2px rgba(15, 23, 42, .04), 0 1px 1px rgba(15, 23, 42, .02);\n'
    '    transition: border-color .12s, box-shadow .12s;\n'
    '  }\n'
    '  .pcard:hover { border-color: #d1d5db; box-shadow: 0 2px 6px rgba(15, 23, 42, .06); }\n'
    '  .pcard-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 14px; }\n'
    '  .pcard-name {\n'
    '    font-size: 16px; font-weight: 700; color: #0f172a; line-height: 1.25;\n'
    '    overflow: hidden; text-overflow: ellipsis;\n'
    '  }\n'
    '  .pcard-phone {\n'
    '    font-family: ui-monospace, "SF Mono", Menlo, monospace;\n'
    '    font-size: 11px; color: #94a3b8; margin-top: 3px; letter-spacing: .02em;\n'
    '  }\n'
    '  .pcard-badge {\n'
    '    background: #eef2ff; color: #4338ca;\n'
    '    padding: 4px 10px; border-radius: 99px;\n'
    '    font-size: 10.5px; font-weight: 700; white-space: nowrap;\n'
    '    border: 1px solid #c7d2fe; line-height: 1.4;\n'
    '  }\n'
    '\n'
    '  .pcard-hero {\n'
    '    position: relative;\n'
    '    background: linear-gradient(135deg, var(--rf-orange-soft, #fff5f3) 0%, #fff 80%);\n'
    '    border: 1px solid #fed7aa; border-radius: 12px;\n'
    '    padding: 14px 16px; margin-bottom: 14px;\n'
    '  }\n'
    '  .pcard-hero.is-done {\n'
    '    background: linear-gradient(135deg, #ecfdf5 0%, #fff 80%);\n'
    '    border-color: #86efac;\n'
    '  }\n'
    '  .pcard-hero-eyebrow {\n'
    '    font-size: 10px; font-weight: 800; letter-spacing: .14em;\n'
    '    text-transform: uppercase; color: var(--rf-orange-dark, #d54b33);\n'
    '  }\n'
    '  .pcard-hero.is-done .pcard-hero-eyebrow { color: #15803d; }\n'
    '  .pcard-hero-title {\n'
    '    font-size: 20px; font-weight: 800; color: #0f172a;\n'
    '    margin: 6px 0 0; line-height: 1.1; letter-spacing: -.01em;\n'
    '  }\n'
    '  .pcard-hero-meta {\n'
    '    display: flex; justify-content: space-between; align-items: baseline;\n'
    '    gap: 8px; flex-wrap: wrap;\n'
    '    font-size: 12.5px; color: #475569; margin: 12px 0 6px;\n'
    '    font-variant-numeric: tabular-nums;\n'
    '  }\n'
    '  .pcard-hero-meta b { color: #0f172a; font-weight: 700; }\n'
    '  .pcard-hero-pct { font-weight: 700; color: var(--rf-orange-dark, #d54b33); }\n'
    '  .pcard-hero.is-done .pcard-hero-pct { color: #15803d; }\n'
    '  .pcard-progress {\n'
    '    height: 8px; background: rgba(15, 23, 42, .06);\n'
    '    border-radius: 99px; overflow: hidden;\n'
    '  }\n'
    '  .pcard-progress > span {\n'
    '    display: block; height: 100%;\n'
    '    background: linear-gradient(90deg, var(--rf-orange, #f6624a), var(--rf-orange-dark, #d54b33));\n'
    '    border-radius: 99px;\n'
    '    transition: width .8s cubic-bezier(.2,.7,.3,1);\n'
    '  }\n'
    '  .pcard-hero.is-done .pcard-progress > span {\n'
    '    background: linear-gradient(90deg, #22c55e, #16a34a);\n'
    '  }\n'
    '  .pcard-hero-remaining { font-size: 11.5px; color: #6b7280; margin-top: 8px; line-height: 1.4; }\n'
    '\n'
    '  .pcard-prizes { margin-top: 14px; }\n'
    '  .pcard-prizes-label {\n'
    '    font-size: 10px; font-weight: 800; letter-spacing: .12em;\n'
    '    text-transform: uppercase; color: #6b7280; margin: 0 0 8px;\n'
    '  }\n'
    '  .pcard-prize-list { display: flex; flex-direction: column; gap: 6px; }\n'
    '  .pcard-prize {\n'
    '    display: flex; align-items: center; gap: 10px;\n'
    '    padding: 8px 10px 8px 8px;\n'
    '    background: #fff;\n'
    '    border: 1px solid #e5e7eb; border-left: 3px solid;\n'
    '    border-radius: 8px;\n'
    '    font-size: 12px;\n'
    '  }\n'
    '  .pcard-prize-medal {\n'
    '    width: 24px; height: 24px; border-radius: 50%;\n'
    '    display: inline-flex; align-items: center; justify-content: center;\n'
    '    font-size: 11px; font-weight: 800; color: #fff;\n'
    '    flex-shrink: 0;\n'
    '    box-shadow: inset 0 1px 2px rgba(255,255,255,.45), 0 1px 2px rgba(0,0,0,.15);\n'
    '  }\n'
    '  .pcard-prize-1 { border-left-color: var(--rf-bronze, #b57032); }\n'
    '  .pcard-prize-1 .pcard-prize-medal { background: linear-gradient(135deg, #d58f4f, var(--rf-bronze, #b57032)); }\n'
    '  .pcard-prize-2 { border-left-color: var(--rf-silver, #6b7b8c); }\n'
    '  .pcard-prize-2 .pcard-prize-medal { background: linear-gradient(135deg, #95a5b5, var(--rf-silver, #6b7b8c)); }\n'
    '  .pcard-prize-3 { border-left-color: var(--rf-gold, #c9a227); }\n'
    '  .pcard-prize-3 .pcard-prize-medal { background: linear-gradient(135deg, #f4d656, var(--rf-gold, #c9a227)); }\n'
    '  .pcard-prize-name {\n'
    '    flex: 1; min-width: 0; color: #1f2937;\n'
    '    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;\n'
    '  }\n'
    '  .pcard-prize-tag {\n'
    '    font-size: 9.5px; font-weight: 800; color: #6b7280;\n'
    '    text-transform: uppercase; letter-spacing: .08em; flex-shrink: 0;\n'
    '  }\n'
    '\n'
    '  .pcard-commit {\n'
    '    padding: 14px;\n'
    '    background: #f9fafb;\n'
    '    border: 1px solid #e5e7eb;\n'
    '    border-radius: 12px;\n'
    '    margin-bottom: 14px;\n'
    '  }\n'
    '  .pcard-commit-row {\n'
    '    display: flex; align-items: center; justify-content: space-between;\n'
    '    gap: 12px;\n'
    '  }\n'
    '  .pcard-commit-label { font-size: 12px; color: #475569; flex: 1; min-width: 0; font-weight: 500; }\n'
    '  .pcard-commit-count {\n'
    '    font-size: 18px; font-weight: 800; color: #0f172a;\n'
    '    font-variant-numeric: tabular-nums; flex-shrink: 0;\n'
    '  }\n'
    '  .pcard-commit-count.is-low { color: #dc2626; }\n'
    '  .pcard-commit-count.is-ok  { color: #16a34a; }\n'
    '  .pcard-commit-count .denom { font-size: 12px; font-weight: 500; color: #94a3b8; }\n'
    '  .pcard-commit-btn {\n'
    '    background: #0f172a; color: #fff;\n'
    '    border: 0; padding: 8px 14px;\n'
    '    border-radius: 8px;\n'
    '    font-size: 12px; font-weight: 600;\n'
    '    cursor: pointer; flex-shrink: 0;\n'
    '    min-height: 36px;\n'
    '    transition: background .12s, transform .08s;\n'
    '  }\n'
    '  .pcard-commit-btn:hover  { background: #1e293b; }\n'
    '  .pcard-commit-btn:active { transform: scale(.97); }\n'
    '  .pcard-commit-bar {\n'
    '    height: 5px; background: #e5e7eb;\n'
    '    border-radius: 99px; margin-top: 10px; overflow: hidden;\n'
    '  }\n'
    '  .pcard-commit-bar > span {\n'
    '    display: block; height: 100%;\n'
    '    background: #3b82f6;\n'
    '    border-radius: 99px;\n'
    '    transition: width .6s cubic-bezier(.2,.7,.3,1);\n'
    '  }\n'
    '  .pcard-commit-bar.is-ok > span { background: #16a34a; }\n'
    '\n'
    '  .pcard-milestones {\n'
    '    padding: 4px 0 0;\n'
    '  }\n'
    '  .pcard-milestones-label {\n'
    '    font-size: 10px; font-weight: 800; letter-spacing: .12em;\n'
    '    text-transform: uppercase; color: #6b7280; margin: 0 0 8px;\n'
    '  }\n'
    '  .pcard-milestone {\n'
    '    display: flex; align-items: center; gap: 12px;\n'
    '    padding: 12px 14px;\n'
    '    border: 1px solid #e5e7eb;\n'
    '    border-radius: 10px;\n'
    '  }\n'
    '  .pcard-milestone + .pcard-milestone { margin-top: 8px; }\n'
    '  .pcard-milestone.is-open { border-color: #86efac; background: #f0fdf4; }\n'
    '  .pcard-milestone-icon {\n'
    '    width: 28px; height: 28px; border-radius: 50%;\n'
    '    display: inline-flex; align-items: center; justify-content: center;\n'
    '    background: #f1f5f9; color: #94a3b8;\n'
    '    font-size: 13px; flex-shrink: 0;\n'
    '  }\n'
    '  .pcard-milestone.is-open .pcard-milestone-icon { background: #dcfce7; color: #16a34a; }\n'
    '  .pcard-milestone-text  { flex: 1; min-width: 0; }\n'
    '  .pcard-milestone-name  { font-size: 13px; font-weight: 700; color: #0f172a; }\n'
    '  .pcard-milestone.is-open .pcard-milestone-name { color: #14532d; }\n'
    '  .pcard-milestone-meta  {\n'
    '    font-size: 11px; color: #6b7280; margin-top: 2px;\n'
    '    display: flex; gap: 10px; flex-wrap: wrap;\n'
    '    font-variant-numeric: tabular-nums;\n'
    '  }\n'
    '  .pcard-milestone-meta b { color: #0f172a; font-weight: 700; }\n'
    '  .pcard-milestone-meta b.is-ok { color: #16a34a; }\n'
    '  .pcard-milestone-status {\n'
    '    font-size: 9.5px; font-weight: 800;\n'
    '    text-transform: uppercase; letter-spacing: .08em;\n'
    '    padding: 4px 8px; border-radius: 99px;\n'
    '    flex-shrink: 0; line-height: 1.4;\n'
    '  }\n'
    '  .pcard-milestone-status.is-open   { background: #dcfce7; color: #15803d; }\n'
    '  .pcard-milestone-status.is-locked { background: #f1f5f9; color: #94a3b8; }\n'
    '\n'
    '  @media (max-width: 768px) {\n'
    '    .pcard { padding: 14px; border-radius: 14px; }\n'
    '    .pcard-name { font-size: 15px; }\n'
    '    .pcard-hero { padding: 12px 14px; }\n'
    '    .pcard-hero-title { font-size: 18px; }\n'
    '    .pcard-prize { padding: 7px 9px 7px 7px; gap: 8px; font-size: 11.5px; }\n'
    '    .pcard-prize-medal { width: 22px; height: 22px; font-size: 10.5px; }\n'
    '    .pcard-commit-count { font-size: 16px; }\n'
    '    .pcard-milestone { padding: 10px 12px; gap: 10px; }\n'
    '    .pcard-milestone-name { font-size: 12.5px; }\n'
    '    .pcard-milestone-icon { width: 26px; height: 26px; }\n'
    '  }\n'
    + CSS_END
)

# Inject new CSS right before the existing RTL Arabic block (carry from prior patches).
css_anchor = '/* === END ROUE DE LA FORTUNE THEME === */'
if css_anchor not in src:
    print('  [FAIL] CSS injection anchor not found'); sys.exit(2)
src = src.replace(css_anchor,
                  css_anchor + nl + '  ' + CSS_BLOCK.replace('\n', nl),
                  1)
print('  [ok]   injected pcard CSS')


# ---- Rewrite the per-client card HTML ----------------------------------
# Anchor: the entire `cardsHtml += \`\n      <div class="pal-card" ...` block
# ending at the two giftRow(...) calls and the closing `;`.
OLD_CARD = (
    "    cardsHtml += `\n"
    "      <div class=\"pal-card\" style=\"background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; margin-bottom:8px;\">\n"
    "        <div style=\"display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap;\">\n"
    "          <div style=\"min-width:0; flex:1;\">\n"
    "            <div style=\"font-weight:700; font-size:13.5px; color:#0f172a; line-height:1.2; overflow:hidden; text-overflow:ellipsis;\">${gmvEscapeHtmlEng(cl.name || '(no name)')}</div>\n"
    "            <div style=\"font-family:monospace; font-size:10.5px; color:#94a3b8; margin-top:1px;\">${gmvEscapeHtmlEng(phone)}</div>\n"
    "          </div>\n"
    "          ${ach ? `<span style=\"background:#dbeafe; color:#1e40af; padding:2px 8px; border-radius:99px; font-size:10px; font-weight:700; white-space:nowrap;\">${engT('pal_achieved')} ${ach.palier}</span>` : ''}\n"
    "        </div>\n"
    "        ${(() => {\n"
    "          if (allDone) {\n"
    "            return `<div style=\"margin-top:8px; padding:6px 10px; border-radius:6px; background:#f0fdf4; border:1px solid #86efac; font-size:11.5px; color:#15803d; font-weight:600; text-align:center;\">${engT('pal_all_done')}</div>`;\n"
    "          }\n"
    "          if (!targetP) return '';\n"
    "          const remaining = Math.max(0, (targetP.threshold || 0) - cBoth);\n"
    "          const progPct = Math.min(100, Math.round((cBoth / (targetP.threshold || 1)) * 100));\n"
    "          const medals = [\n"
    "            { cls: 'rf-medal-1', label: engT('rf_medal_1'), prize: targetP.prize1 || '' },\n"
    "            { cls: 'rf-medal-2', label: engT('rf_medal_2'), prize: targetP.prize2 || '' },\n"
    "            { cls: 'rf-medal-3', label: engT('rf_medal_3'), prize: targetP.prize3 || '' },\n"
    "          ].filter(m => m.prize);\n"
    "          const medalsHtml = medals.length\n"
    "            ? `<div class=\"rf-medals\" title=\"${engT('rf_prizes')}\">${medals.map((m, i) => `<span class=\"rf-medal ${m.cls}\"><span class=\"rf-medal-dot\">${i + 1}</span><span class=\"rf-medal-name\" title=\"${gmvEscapeHtmlEng(m.prize)}\">${gmvEscapeHtmlEng(m.prize)}</span></span>`).join('')}</div>`\n"
    "            : '';\n"
    "          return `<div style=\"margin-top:8px; padding-top:8px; border-top:1px solid #f1f5f9;\">\n"
    "            <div style=\"display:flex; justify-content:space-between; align-items:baseline; font-size:11.5px; gap:8px; flex-wrap:wrap;\">\n"
    "              <span style=\"color:#64748b;\">${engT('pal_next_target')} : <b style=\"color:#0f172a;\">${engT('pal_lvl', { n: targetP.palier })}</b></span>\n"
    "              <span style=\"color:#64748b; font-size:10.5px;\"><b style=\"color:#0f172a;\">${fmt(cBoth)}</b> / ${fmt(targetP.threshold)} MAD</span>\n"
    "            </div>\n"
    "            <div style=\"height:3px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:5px;\">\n"
    "              <div style=\"height:100%; width:${progPct}%; background:var(--rf-orange); transition:width .4s;\"></div>\n"
    "            </div>\n"
    "            <div style=\"font-size:10.5px; color:#64748b; margin-top:3px;\">${engT('pal_remaining', { n: fmt(remaining) })}</div>\n"
    "            ${medalsHtml}\n"
    "          </div>`;\n"
    "        })()}\n"
    "        <div style=\"margin-top:8px; padding-top:8px; border-top:1px solid #f1f5f9;\">\n"
    "          <div style=\"display:flex; justify-content:space-between; align-items:center; font-size:11.5px; gap:8px;\">\n"
    "            <span style=\"color:#64748b;\">${engT('pal_my_products')} : <b style=\"color:${prodOk ? '#16a34a' : '#dc2626'};\">${myProds.length}</b><span style=\"color:#94a3b8;\"> / ${ENG_CLIENT_MIN_PRODUCTS}</span></span>\n"
    "            <button type=\"button\" data-pal-edit=\"${gmvEscapeHtmlEng(phone)}\" style=\"background:#0f172a; border:0; color:#fff; padding:4px 10px; border-radius:6px; font-size:10.5px; font-weight:600; cursor:pointer;\">${engT('pal_edit')}</button>\n"
    "          </div>\n"
    "          <div style=\"height:3px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:4px;\">\n"
    "            <div style=\"height:100%; width:${prodPct}%; background:${prodOk ? '#16a34a' : '#3b82f6'}; transition:width .4s;\"></div>\n"
    "          </div>\n"
)

NEW_CARD = (
    "    // ===== HERO (next palier) + medals =====\n"
    "    const _heroBlock = (() => {\n"
    "      if (allDone) {\n"
    "        return `<section class=\"pcard-hero is-done\">\n"
    "          <div class=\"pcard-hero-eyebrow\">🏆 ${engT('pal_all_done')}</div>\n"
    "        </section>`;\n"
    "      }\n"
    "      if (!targetP) return '';\n"
    "      const remaining = Math.max(0, (targetP.threshold || 0) - cBoth);\n"
    "      const progPct = Math.min(100, Math.round((cBoth / (targetP.threshold || 1)) * 100));\n"
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
    "        : '';\n"
    "      return `<section class=\"pcard-hero\">\n"
    "        <div class=\"pcard-hero-eyebrow\">${engT('pal_next_target')}</div>\n"
    "        <div class=\"pcard-hero-title\">${engT('pal_lvl', { n: targetP.palier })}</div>\n"
    "        <div class=\"pcard-hero-meta\">\n"
    "          <span><b>${fmt(cBoth)}</b> / ${fmt(targetP.threshold)} MAD</span>\n"
    "          <span class=\"pcard-hero-pct\">${progPct}%</span>\n"
    "        </div>\n"
    "        <div class=\"pcard-progress\"><span style=\"width:${progPct}%\"></span></div>\n"
    "        <div class=\"pcard-hero-remaining\">${engT('pal_remaining', { n: fmt(remaining) })}</div>\n"
    "        ${_prizesHtml}\n"
    "      </section>`;\n"
    "    })();\n"
    "\n"
    "    // ===== MILESTONES =====\n"
    "    const _milestone = (open, count, total, label, gmvCur, gmvTgt) => `\n"
    "      <div class=\"pcard-milestone${open ? ' is-open' : ''}\">\n"
    "        <span class=\"pcard-milestone-icon\">${open ? '✓' : '🔒'}</span>\n"
    "        <div class=\"pcard-milestone-text\">\n"
    "          <div class=\"pcard-milestone-name\">${label}</div>\n"
    "          <div class=\"pcard-milestone-meta\">\n"
    "            <span><b class=\"${count >= total ? 'is-ok' : ''}\">${count}</b> / ${total} ${engT('pal_products')}</span>\n"
    "            ${gmvTgt ? `<span><b class=\"${gmvCur >= gmvTgt ? 'is-ok' : ''}\">${fmt(gmvCur)}</b> / ${fmt(gmvTgt)} MAD</span>` : ''}\n"
    "          </div>\n"
    "        </div>\n"
    "        <span class=\"pcard-milestone-status ${open ? 'is-open' : 'is-locked'}\">${open ? engT('pal_gift_open') : engT('pal_gift_locked')}</span>\n"
    "      </div>`;\n"
    "\n"
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
    "        <section class=\"pcard-commit\">\n"
    "          <div class=\"pcard-commit-row\">\n"
    "            <div class=\"pcard-commit-label\">${engT('pal_my_products')}</div>\n"
    "            <div class=\"pcard-commit-count ${prodOk ? 'is-ok' : 'is-low'}\">${myProds.length}<span class=\"denom\"> / ${ENG_CLIENT_MIN_PRODUCTS}</span></div>\n"
    "            <button type=\"button\" data-pal-edit=\"${gmvEscapeHtmlEng(phone)}\" class=\"pcard-commit-btn\">${engT('pal_edit')}</button>\n"
    "          </div>\n"
    "          <div class=\"pcard-commit-bar${prodOk ? ' is-ok' : ''}\"><span style=\"width:${prodPct}%\"></span></div>\n"
)

src = go(src, OLD_CARD, NEW_CARD, 'rewrite per-client card (header + hero + commit)')


# ---- Replace the closing tail of the card (gift rows -> milestones list)
OLD_TAIL = (
    "          </div>\n"
    "        </div>\n"
    "        ${giftRow(engT('pal_may_gift'),  m1Count,   ENG_CLIENT_MILESTONE_M1,   m1Pct,   m1Open,   cM1,   targetP ? targetP.threshold : 0)}\n"
    "        ${giftRow(engT('pal_both_gift'), bothCount, ENG_CLIENT_MILESTONE_BOTH, bothPct, bothOpen, cBoth, targetP ? targetP.threshold : 0)}\n"
    "      </div>`;\n"
)
NEW_TAIL = (
    "          </div>\n"
    "        </section>\n"
    "        <section class=\"pcard-milestones\">\n"
    "          <div class=\"pcard-milestones-label\">${engT('pal_milestones')}</div>\n"
    "          ${_milestone(m1Open,   m1Count,   ENG_CLIENT_MILESTONE_M1,   engT('pal_may_gift'),  cM1,   targetP ? targetP.threshold : 0)}\n"
    "          ${_milestone(bothOpen, bothCount, ENG_CLIENT_MILESTONE_BOTH, engT('pal_both_gift'), cBoth, targetP ? targetP.threshold : 0)}\n"
    "        </section>\n"
    "      </article>`;\n"
)
src = go(src, OLD_TAIL, NEW_TAIL, 'rewrite per-client card tail (milestones list)')


# ---- Add the i18n key pal_milestones in FR/EN/AR ------------------------
src = go(src,
    "    pal_search: 'Rechercher un client...', pal_no_match: 'Aucun client ne correspond à la recherche.',\n",
    "    pal_search: 'Rechercher un client...', pal_no_match: 'Aucun client ne correspond à la recherche.',\n"
    "    pal_milestones: 'Jalons de la campagne',\n",
    'FR pal_milestones')

src = go(src,
    "    pal_search: 'Search clients...', pal_no_match: 'No clients match the search.',\n",
    "    pal_search: 'Search clients...', pal_no_match: 'No clients match the search.',\n"
    "    pal_milestones: 'Campaign milestones',\n",
    'EN pal_milestones')

src = go(src,
    "    pal_search: 'البحث عن زبون...', pal_no_match: 'لا يوجد زبون يطابق البحث.',\n",
    "    pal_search: 'البحث عن زبون...', pal_no_match: 'لا يوجد زبون يطابق البحث.',\n"
    "    pal_milestones: 'مراحل الحملة',\n",
    'AR pal_milestones')


if fails:
    print('FAIL — not writing. ' + str(len(fails)) + ' step(s) failed.')
    sys.exit(2)

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
