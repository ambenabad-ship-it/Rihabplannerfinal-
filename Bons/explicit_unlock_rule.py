# -*- coding: utf-8 -*-
"""
Rewrite the milestone row so the two-condition AND-rule is explicit:

  Cadeau Mai 2026                              🔒 Verrouillé
    ✓  5 produits au min MAD en Mai              5 / 5
    ✗  CA Mai ≥ seuil du palier      124,500 / 150,000 MAD

  Both must be met for the gift to unlock. When both ✓, the row flips
  to green and the status pill becomes "Débloqué".
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


# ---- 1) CSS: condition rows + AND separator --------------------------
CSS_BEGIN = '/* === EXPLICIT UNLOCK RULE — explicit_unlock_rule.py === */'
CSS_END   = '/* === END EXPLICIT UNLOCK RULE === */'
src = strip_block(src, CSS_BEGIN, CSS_END)

CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  /* Two-condition milestone restructure. */\n'
    '  .pcard-milestone-v2 {\n'
    '    border: 1px solid #e5e7eb;\n'
    '    border-radius: 10px;\n'
    '    overflow: hidden;\n'
    '  }\n'
    '  .pcard-milestone-v2 + .pcard-milestone-v2 { margin-top: 8px; }\n'
    '  .pcard-milestone-v2.is-open { border-color: #86efac; }\n'
    '\n'
    '  .pcard-milestone-v2-head {\n'
    '    display: flex; align-items: center; gap: 10px;\n'
    '    padding: 10px 12px;\n'
    '    background: #fafafa;\n'
    '    border-bottom: 1px solid #e5e7eb;\n'
    '  }\n'
    '  .pcard-milestone-v2.is-open .pcard-milestone-v2-head { background: #f0fdf4; border-bottom-color: #86efac; }\n'
    '  .pcard-milestone-v2-icon {\n'
    '    width: 28px; height: 28px; border-radius: 50%;\n'
    '    display: inline-flex; align-items: center; justify-content: center;\n'
    '    background: #fff7ed; color: #c2410c;\n'
    '    box-shadow: inset 0 0 0 1px #fed7aa;\n'
    '    font-size: 14px; flex-shrink: 0;\n'
    '  }\n'
    '  .pcard-milestone-v2.is-open .pcard-milestone-v2-icon {\n'
    '    background: #dcfce7; color: #15803d; box-shadow: inset 0 0 0 1px #86efac;\n'
    '  }\n'
    '  .pcard-milestone-v2-text { flex: 1; min-width: 0; }\n'
    '  .pcard-milestone-v2-name {\n'
    '    font-size: 13px; font-weight: 700; color: #0f172a; line-height: 1.2;\n'
    '  }\n'
    '  .pcard-milestone-v2.is-open .pcard-milestone-v2-name { color: #14532d; }\n'
    '  .pcard-milestone-v2-sub {\n'
    '    font-size: 10.5px; color: #6b7280; margin-top: 2px;\n'
    '  }\n'
    '\n'
    '  .pcard-milestone-v2-conds { padding: 6px 0; background: #fff; }\n'
    '  .pcard-milestone-v2.is-open .pcard-milestone-v2-conds { background: #f0fdf4; }\n'
    '  .pcard-mile-cond {\n'
    '    display: flex; align-items: center; gap: 10px;\n'
    '    padding: 9px 12px;\n'
    '    font-size: 12px;\n'
    '  }\n'
    '  .pcard-mile-cond + .pcard-mile-cond {\n'
    '    border-top: 1px solid #f1f5f9;\n'
    '  }\n'
    '  .pcard-milestone-v2.is-open .pcard-mile-cond + .pcard-mile-cond { border-top-color: #bbf7d0; }\n'
    '  .pcard-mile-cond-icon {\n'
    '    width: 20px; height: 20px; border-radius: 50%;\n'
    '    display: inline-flex; align-items: center; justify-content: center;\n'
    '    font-size: 11px; font-weight: 800; flex-shrink: 0;\n'
    '    background: #f1f5f9; color: #94a3b8;\n'
    '  }\n'
    '  .pcard-mile-cond.is-met .pcard-mile-cond-icon {\n'
    '    background: #16a34a; color: #fff;\n'
    '  }\n'
    '  .pcard-mile-cond-text {\n'
    '    flex: 1; min-width: 0; color: #475569; line-height: 1.35;\n'
    '  }\n'
    '  .pcard-mile-cond.is-met .pcard-mile-cond-text { color: #14532d; font-weight: 600; }\n'
    '  .pcard-mile-cond-value {\n'
    '    font-size: 11.5px; font-variant-numeric: tabular-nums; color: #0f172a;\n'
    '    flex-shrink: 0; white-space: nowrap;\n'
    '  }\n'
    '  .pcard-mile-cond-value b { font-weight: 800; }\n'
    '  .pcard-mile-cond.is-met .pcard-mile-cond-value b { color: #16a34a; }\n'
    '\n'
    '  .pcard-milestone-v2-status {\n'
    '    font-size: 9.5px; font-weight: 800;\n'
    '    text-transform: uppercase; letter-spacing: .08em;\n'
    '    padding: 4px 9px; border-radius: 99px;\n'
    '    flex-shrink: 0; line-height: 1.4;\n'
    '    background: #f1f5f9; color: #94a3b8;\n'
    '  }\n'
    '  .pcard-milestone-v2.is-open .pcard-milestone-v2-status {\n'
    '    background: #dcfce7; color: #15803d;\n'
    '  }\n'
    + CSS_END
)

css_anchor = '/* === END CAMPAIGN MONTHS LABEL === */'
if css_anchor not in src:
    print('  [FAIL] CSS anchor not found'); sys.exit(2)
src = src.replace(css_anchor, css_anchor + nl + '  ' + CSS_BLOCK.replace('\n', nl), 1)
print('  [ok]   injected explicit-rule CSS')


# ---- 2) Rewrite _milestone helper to render the two-condition layout --
OLD_HELPER = (
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
)

NEW_HELPER = (
    "    // ===== MILESTONES (two-condition checklist) =====\n"
    "    // periodLabel — 'Mai' / 'Mai+Juin' to make the GMV window explicit.\n"
    "    const _milestone = (open, count, total, label, gmvCur, gmvTgt, periodLabel) => {\n"
    "      const prodMet = count >= total;\n"
    "      const gmvMet  = !!gmvTgt && gmvCur >= gmvTgt;\n"
    "      const _check = met => `<span class=\"pcard-mile-cond-icon\">${met ? '✓' : '✗'}</span>`;\n"
    "      const prodLine = `\n"
    "        <div class=\"pcard-mile-cond${prodMet ? ' is-met' : ''}\">\n"
    "          ${_check(prodMet)}\n"
    "          <span class=\"pcard-mile-cond-text\">${engT('pal_cond_products', { n: total, period: periodLabel })}</span>\n"
    "          <span class=\"pcard-mile-cond-value\"><b>${count}</b> / ${total}</span>\n"
    "        </div>`;\n"
    "      const gmvLine = `\n"
    "        <div class=\"pcard-mile-cond${gmvMet ? ' is-met' : ''}\">\n"
    "          ${_check(gmvMet)}\n"
    "          <span class=\"pcard-mile-cond-text\">${engT('pal_cond_gmv', { period: periodLabel })}</span>\n"
    "          <span class=\"pcard-mile-cond-value\">${gmvTgt ? `<b>${fmt(gmvCur)}</b> / ${fmt(gmvTgt)} MAD` : `<span style=\"color:#dc2626;\">${engT('pal_no_target_set')}</span>`}</span>\n"
    "        </div>`;\n"
    "      return `\n"
    "        <div class=\"pcard-milestone-v2${open ? ' is-open' : ''}\">\n"
    "          <div class=\"pcard-milestone-v2-head\">\n"
    "            <span class=\"pcard-milestone-v2-icon\">${open ? '🎁' : '🔒'}</span>\n"
    "            <div class=\"pcard-milestone-v2-text\">\n"
    "              <div class=\"pcard-milestone-v2-name\">${label}</div>\n"
    "              <div class=\"pcard-milestone-v2-sub\">${engT('pal_rule_both')}</div>\n"
    "            </div>\n"
    "            <span class=\"pcard-milestone-v2-status\">${open ? engT('pal_gift_open') : engT('pal_gift_locked')}</span>\n"
    "          </div>\n"
    "          <div class=\"pcard-milestone-v2-conds\">\n"
    "            ${prodLine}\n"
    "            ${gmvLine}\n"
    "          </div>\n"
    "        </div>`;\n"
    "    };\n"
)

src = go(src, OLD_HELPER, NEW_HELPER, 'two-condition milestone helper')


# ---- 3) Update call sites to pass the period label --------------------
src = go(src,
    "          ${_milestone(m1Open,   m1Count,   ENG_CLIENT_MILESTONE_M1,   engT('pal_may_gift'),  cM1,   targetP ? targetP.threshold : 0)}\n"
    "          ${_milestone(bothOpen, bothCount, ENG_CLIENT_MILESTONE_BOTH, engT('pal_both_gift'), cBoth, targetP ? targetP.threshold : 0)}\n",
    "          ${_milestone(m1Open,   m1Count,   ENG_CLIENT_MILESTONE_M1,   engT('pal_may_gift'),  cM1,   targetP ? targetP.threshold : 0, engT('pal_month_may'))}\n"
    "          ${_milestone(bothOpen, bothCount, ENG_CLIENT_MILESTONE_BOTH, engT('pal_both_gift'), cBoth, targetP ? targetP.threshold : 0, engT('pal_month_may') + ' + ' + engT('pal_month_june'))}\n",
    'pass period labels to milestone calls')


# ---- 4) New i18n keys ------------------------------------------------
def add_after(s, anchor, addition, label):
    o = anchor.replace('\n', nl)
    n = o + addition.replace('\n', nl)
    if n in s and o not in s: print('  [skip] ' + label); return s
    if o not in s: print('  [FAIL] ' + label); sys.exit(2)
    if s.count(o) != 1: print('  [FAIL] ' + label + ' (count ' + str(s.count(o)) + ')'); sys.exit(2)
    print('  [ok]   ' + label)
    return s.replace(o, n, 1)

src = add_after(src,
    "    pal_month_may: 'Mai 2026', pal_month_june: 'Juin 2026',\n",
    "    pal_rule_both: 'Les 2 conditions ci-dessous doivent être atteintes.',\n"
    "    pal_cond_products: '{n} produits au minimum MAD livrés ({period})',\n"
    "    pal_cond_gmv: 'CA du client ≥ seuil du palier ({period})',\n",
    'FR pal_rule_both + condition labels')

src = add_after(src,
    "    pal_month_may: 'May 2026', pal_month_june: 'June 2026',\n",
    "    pal_rule_both: 'Both conditions below must be met.',\n"
    "    pal_cond_products: '{n} products at the MAD minimum delivered ({period})',\n"
    "    pal_cond_gmv: \"Client's GMV ≥ palier threshold ({period})\",\n",
    'EN pal_rule_both + condition labels')

src = add_after(src,
    "    pal_month_may: 'ماي 2026', pal_month_june: 'يونيو 2026',\n",
    "    pal_rule_both: 'يجب تحقيق الشرطين التاليين معا.',\n"
    "    pal_cond_products: '{n} منتج بالحد الأدنى للدرهم تم تسليمها ({period})',\n"
    "    pal_cond_gmv: 'CA الزبون ≥ عتبة المستوى ({period})',\n",
    'AR pal_rule_both + condition labels')


io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
