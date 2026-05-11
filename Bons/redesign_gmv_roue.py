# -*- coding: utf-8 -*-
"""
GMV Tracker / Engagement re-skin — inspired by Roue de la Fortune brochure.

Adds:
  * Orange (#F6624A) hero band at the top of the Engagement panel with an
    animated dashed-circle decoration + 4-step "how it works" row.
  * Animated mini fortune wheel SVG inside the hero (bronze/silver/gold
    conic gradient, slow spin, gold rim, pointer + hub).
  * Bronze/Silver/Gold prize medals next to each next-target palier on the
    per-client paliers card so sellers see the actual rewards.
  * Reusable CSS tokens (--rf-orange, --rf-bronze, --rf-silver, --rf-gold).

Idempotent. Single-pass write.
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


CSS_BEGIN = '/* === ROUE DE LA FORTUNE THEME — redesign_gmv_roue.py === */'
CSS_END   = '/* === END ROUE DE LA FORTUNE THEME === */'

src = strip_block(src, CSS_BEGIN, CSS_END)

CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  :root {\n'
    '    --rf-orange:       #F6624A;\n'
    '    --rf-orange-dark:  #D54B33;\n'
    '    --rf-orange-light: #FFE8E2;\n'
    '    --rf-orange-soft:  #FFF5F3;\n'
    '    --rf-green:        #3B8083;\n'
    '    --rf-bronze:       #B57032;\n'
    '    --rf-silver:       #6B7B8C;\n'
    '    --rf-gold:         #C9A227;\n'
    '  }\n'
    '\n'
    '  /* ---------- Engagement campaign hero band ---------- */\n'
    '  .rf-hero {\n'
    '    position: relative;\n'
    '    background: linear-gradient(135deg, var(--rf-orange) 0%, var(--rf-orange-dark) 100%);\n'
    '    color: #fff;\n'
    '    border-radius: 14px;\n'
    '    padding: 18px 22px;\n'
    '    margin: 0 0 14px;\n'
    '    overflow: hidden;\n'
    '    box-shadow: 0 4px 14px rgba(246, 98, 74, 0.18);\n'
    '  }\n'
    '  .rf-hero::before {\n'
    '    content: "";\n'
    '    position: absolute;\n'
    '    inset-inline-end: -60px;\n'
    '    top: -60px;\n'
    '    width: 200px; height: 200px;\n'
    '    border-radius: 50%;\n'
    '    border: 10px dashed rgba(255, 255, 255, 0.18);\n'
    '    animation: rf-spin 60s linear infinite;\n'
    '    pointer-events: none;\n'
    '  }\n'
    '  @keyframes rf-spin { to { transform: rotate(360deg); } }\n'
    '  .rf-hero-inner {\n'
    '    position: relative; z-index: 1;\n'
    '    display: flex; align-items: center; gap: 20px; flex-wrap: wrap;\n'
    '  }\n'
    '  .rf-hero-text { flex: 1; min-width: 200px; }\n'
    '  .rf-hero-pill {\n'
    '    display: inline-block;\n'
    '    background: rgba(255,255,255,0.22);\n'
    '    padding: 3px 10px; border-radius: 99px;\n'
    '    font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em;\n'
    '    font-weight: 700; margin-bottom: 8px;\n'
    '  }\n'
    '  .rf-hero-title { font-size: 22px; font-weight: 800; margin: 0; line-height: 1.15; letter-spacing: -0.01em; }\n'
    '  .rf-hero-sub   { font-size: 12.5px; opacity: 0.92; margin: 4px 0 0; line-height: 1.4; }\n'
    '\n'
    '  /* ---------- Mini fortune wheel ---------- */\n'
    '  .rf-wheel { width: 96px; height: 96px; flex-shrink: 0; position: relative; filter: drop-shadow(0 4px 14px rgba(0,0,0,0.18)); }\n'
    '  .rf-wheel-rim {\n'
    '    position: absolute; inset: -3px; border-radius: 50%;\n'
    '    background: conic-gradient(from 0deg, #FFD27A, #C9A227, #FFD27A, #B57032, #FFD27A, #6B7B8C, #FFD27A, #B57032, #FFD27A, #C9A227, #FFD27A);\n'
    '    animation: rf-spin 30s linear infinite;\n'
    '    box-shadow: 0 0 14px rgba(201, 162, 39, 0.55), inset 0 0 8px rgba(0,0,0,0.18);\n'
    '  }\n'
    '  .rf-wheel-inner {\n'
    '    width: 100%; height: 100%; border-radius: 50%; position: relative; overflow: hidden;\n'
    '    box-shadow: inset 0 0 0 2px #fff, inset 0 4px 10px rgba(255,255,255,0.45), inset 0 -8px 18px rgba(0,0,0,0.20);\n'
    '    animation: rf-spin 30s linear infinite;\n'
    '    background: conic-gradient(from 0deg, #B57032 0deg, #D58F4F 60deg, #B57032 120deg, #6B7B8C 120deg, #95A5B5 180deg, #6B7B8C 240deg, #C9A227 240deg, #F4D656 300deg, #C9A227 360deg);\n'
    '  }\n'
    '  .rf-wheel-inner::before {\n'
    '    content: ""; position: absolute; inset: 0; border-radius: 50%;\n'
    '    background: radial-gradient(ellipse at 30% 25%, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0) 35%), radial-gradient(ellipse at 70% 75%, rgba(0,0,0,0.18) 0%, rgba(0,0,0,0) 50%);\n'
    '    pointer-events: none;\n'
    '  }\n'
    '  .rf-wheel-hub {\n'
    '    position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);\n'
    '    width: 42px; height: 42px; border-radius: 50%;\n'
    '    background: radial-gradient(circle at 35% 30%, #fff 0%, #fdf3eb 60%, #ffd6c8 100%);\n'
    '    display: flex; align-items: center; justify-content: center;\n'
    '    font-family: "Times New Roman", serif; color: var(--rf-orange-dark);\n'
    '    font-size: 22px; font-weight: 800; font-style: italic;\n'
    '    box-shadow: 0 0 0 3px var(--rf-orange), 0 0 0 4px #fff, 0 0 12px rgba(246,98,74,0.45);\n'
    '    z-index: 3;\n'
    '  }\n'
    '  .rf-wheel-pointer {\n'
    '    position: absolute; top: -8px; left: 50%; transform: translateX(-50%);\n'
    '    width: 0; height: 0;\n'
    '    border-left: 9px solid transparent; border-right: 9px solid transparent;\n'
    '    border-top: 16px solid var(--rf-orange-dark);\n'
    '    z-index: 4; filter: drop-shadow(0 2px 3px rgba(0,0,0,0.30));\n'
    '  }\n'
    '\n'
    '  /* ---------- "How it works" 4-step row ---------- */\n'
    '  .rf-steps {\n'
    '    display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;\n'
    '    margin: 0 0 14px;\n'
    '  }\n'
    '  .rf-step {\n'
    '    position: relative; padding: 10px 12px 10px 38px;\n'
    '    background: #fff; border: 1px solid #e5e7eb; border-radius: 10px;\n'
    '  }\n'
    '  .rf-step-num {\n'
    '    position: absolute; left: 10px; top: 50%; transform: translateY(-50%);\n'
    '    width: 22px; height: 22px; border-radius: 50%;\n'
    '    background: var(--rf-orange); color: #fff;\n'
    '    display: flex; align-items: center; justify-content: center;\n'
    '    font-weight: 800; font-size: 11.5px;\n'
    '  }\n'
    '  .rf-step-title { margin: 0; font-size: 11.5px; font-weight: 800; color: #111827; line-height: 1.2; }\n'
    '  .rf-step-desc  { margin: 2px 0 0; font-size: 10.5px; color: #6B7280; line-height: 1.3; }\n'
    '  @media (max-width: 768px) {\n'
    '    .rf-steps { grid-template-columns: 1fr 1fr; }\n'
    '    .rf-hero-title { font-size: 18px; }\n'
    '  }\n'
    '  @media (max-width: 480px) {\n'
    '    .rf-steps { grid-template-columns: 1fr; }\n'
    '  }\n'
    '\n'
    '  /* ---------- Bronze / Silver / Gold prize chips ---------- */\n'
    '  .rf-medals { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }\n'
    '  .rf-medal {\n'
    '    display: inline-flex; align-items: center; gap: 6px;\n'
    '    padding: 4px 10px 4px 6px; border-radius: 99px;\n'
    '    background: #fff; border: 1px solid var(--rf-border, #e5e7eb);\n'
    '    font-size: 10.5px; font-weight: 600; color: #1f2937;\n'
    '    max-width: 100%; min-width: 0;\n'
    '  }\n'
    '  .rf-medal .rf-medal-dot {\n'
    '    width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0;\n'
    '    box-shadow: inset 0 1px 2px rgba(255,255,255,0.45), 0 1px 2px rgba(0,0,0,0.15);\n'
    '    display: inline-flex; align-items: center; justify-content: center;\n'
    '    font-size: 8px; color: #fff; font-weight: 800;\n'
    '  }\n'
    '  .rf-medal-1 { border-color: var(--rf-bronze); }\n'
    '  .rf-medal-1 .rf-medal-dot { background: linear-gradient(135deg, #D58F4F, var(--rf-bronze)); }\n'
    '  .rf-medal-2 { border-color: var(--rf-silver); }\n'
    '  .rf-medal-2 .rf-medal-dot { background: linear-gradient(135deg, #95A5B5, var(--rf-silver)); }\n'
    '  .rf-medal-3 { border-color: var(--rf-gold); }\n'
    '  .rf-medal-3 .rf-medal-dot { background: linear-gradient(135deg, #F4D656, var(--rf-gold)); }\n'
    '  .rf-medal-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 180px; }\n'
    + CSS_END
)

css_anchor = '/* === END ENGAGEMENT REDESIGN === */  /* RTL fine-tuning for Arabic */' + nl
if css_anchor not in src:
    print('  [FAIL] global CSS anchor not found'); sys.exit(2)
src = src.replace(css_anchor, nl + '  ' + CSS_BLOCK.replace('\n', nl) + nl + css_anchor, 1)
print('  [ok]   injected ROUE DE LA FORTUNE css')


# ---- Add i18n for Roue de la Fortune copy --------------------------------
src = go(src,
    "    pal_target: 'Palier ciblé', pal_my_products: 'Mes produits engagés',\n",
    "    pal_target: 'Palier ciblé', pal_my_products: 'Mes produits engagés',\n"
    "    rf_title: 'Roue de la Fortune', rf_sub: \"Trade Marketing · Wholesale · Mai-Juin 2026\",\n"
    "    rf_pill: '14 paliers · 3 cadeaux par palier',\n"
    "    rf_step1_t: 'Engagement signé', rf_step1_d: 'Cible 100K → 2,5M MAD sur Mai+Juin.',\n"
    "    rf_step2_t: '10 produits focus', rf_step2_d: 'Atteindre le min. MAD sur ≥10 références.',\n"
    "    rf_step3_t: 'Atteinte du palier', rf_step3_d: 'Le GMV cumulé débloque le palier.',\n"
    "    rf_step4_t: 'Tour de roue 🎡', rf_step4_d: '1 cadeau gagné parmi 3 (Bronze/Silver/Gold).',\n"
    "    rf_medal_1: 'Bronze', rf_medal_2: 'Silver', rf_medal_3: 'Gold',\n"
    "    rf_prizes: 'Cadeaux possibles',\n",
    'FR Roue de la Fortune i18n')

src = go(src,
    "    pal_target: 'Target palier', pal_my_products: 'My committed products',\n",
    "    pal_target: 'Target palier', pal_my_products: 'My committed products',\n"
    "    rf_title: 'Fortune Wheel', rf_sub: 'Trade Marketing · Wholesale · May-June 2026',\n"
    "    rf_pill: '14 paliers · 3 prizes per palier',\n"
    "    rf_step1_t: 'Engagement signed', rf_step1_d: 'Target 100K → 2.5M MAD across May+June.',\n"
    "    rf_step2_t: '10 focus products', rf_step2_d: 'Hit the MAD min on ≥10 SKUs.',\n"
    "    rf_step3_t: 'Reach the palier', rf_step3_d: 'Cumulative GMV unlocks the palier.',\n"
    "    rf_step4_t: 'Spin the wheel 🎡', rf_step4_d: '1 prize won among 3 (Bronze/Silver/Gold).',\n"
    "    rf_medal_1: 'Bronze', rf_medal_2: 'Silver', rf_medal_3: 'Gold',\n"
    "    rf_prizes: 'Possible prizes',\n",
    'EN Roue de la Fortune i18n')

src = go(src,
    "    pal_target: 'المستوى المستهدف', pal_my_products: 'منتجاتي الملتزم بها',\n",
    "    pal_target: 'المستوى المستهدف', pal_my_products: 'منتجاتي الملتزم بها',\n"
    "    rf_title: 'عجلة الحظ', rf_sub: \"Trade Marketing · ماي-يونيو 2026\",\n"
    "    rf_pill: '14 مستوى · 3 هدايا لكل مستوى',\n"
    "    rf_step1_t: 'الالتزام موقع', rf_step1_d: 'الهدف 100K → 2.5M درهم على ماي+يونيو.',\n"
    "    rf_step2_t: '10 منتجات مختارة', rf_step2_d: 'الوصول للحد الأدنى بالدرهم على ≥10 منتجات.',\n"
    "    rf_step3_t: 'بلوغ المستوى', rf_step3_d: 'GMV التراكمي يفتح المستوى.',\n"
    "    rf_step4_t: 'دور العجلة 🎡', rf_step4_d: 'هدية واحدة من 3 (برونزية/فضية/ذهبية).',\n"
    "    rf_medal_1: 'برونزية', rf_medal_2: 'فضية', rf_medal_3: 'ذهبية',\n"
    "    rf_prizes: 'الهدايا الممكنة',\n",
    'AR Roue de la Fortune i18n')


# ---- Replace the engagement panel header HTML --------------------------
OLD_HEADER = (
    "  wrap.innerHTML = `\n"
    "    <div style=\"margin:0 0 14px;\">\n"
    "      <h2 style=\"margin:0 0 4px; font-size:18px; font-weight:700;\">${engT('eng_title')}</h2>\n"
    "      <div style=\"font-size:12px; color:#64748b;\">${engT('eng_period_label')} <b>${gmvCurrentPeriodKey()}</b>${mySeller ? ` · ${engT('eng_seller_label')} <b>${gmvEscapeHtmlEng(mySeller)}</b>` : ''}</div>\n"
    "    </div>\n"
    "    ${uploadsHtml}\n"
    "    <div class=\"gmv-engtab-bar\" role=\"tablist\">\n"
    "      ${tabBtn('focus', engT('eng_subtab_focus'))}\n"
    "      ${tabBtn('paliers', engT('eng_subtab_paliers'))}\n"
    "      ${tabBtn('scoreboard', engT('eng_subtab_score'))}\n"
    "    </div>\n"
    "    <div id=\"engPanel\"></div>`;\n"
)

NEW_HEADER = (
    "  // Roue de la Fortune hero — orange band with mini wheel + steps.\n"
    "  const rfHero = `\n"
    "    <section class=\"rf-hero\">\n"
    "      <div class=\"rf-hero-inner\">\n"
    "        <div class=\"rf-wheel\" aria-hidden=\"true\">\n"
    "          <div class=\"rf-wheel-rim\"></div>\n"
    "          <div class=\"rf-wheel-pointer\"></div>\n"
    "          <div class=\"rf-wheel-inner\"></div>\n"
    "          <div class=\"rf-wheel-hub\">z</div>\n"
    "        </div>\n"
    "        <div class=\"rf-hero-text\">\n"
    "          <span class=\"rf-hero-pill\">${engT('rf_pill')}</span>\n"
    "          <h2 class=\"rf-hero-title\">🎡 ${engT('rf_title')}</h2>\n"
    "          <p class=\"rf-hero-sub\">${engT('rf_sub')}${mySeller ? ' · ' + engT('eng_seller_label') + ' ' + gmvEscapeHtmlEng(mySeller) : ''}</p>\n"
    "        </div>\n"
    "      </div>\n"
    "    </section>\n"
    "    <div class=\"rf-steps\">\n"
    "      <div class=\"rf-step\"><span class=\"rf-step-num\">1</span><div class=\"rf-step-title\">${engT('rf_step1_t')}</div><div class=\"rf-step-desc\">${engT('rf_step1_d')}</div></div>\n"
    "      <div class=\"rf-step\"><span class=\"rf-step-num\">2</span><div class=\"rf-step-title\">${engT('rf_step2_t')}</div><div class=\"rf-step-desc\">${engT('rf_step2_d')}</div></div>\n"
    "      <div class=\"rf-step\"><span class=\"rf-step-num\">3</span><div class=\"rf-step-title\">${engT('rf_step3_t')}</div><div class=\"rf-step-desc\">${engT('rf_step3_d')}</div></div>\n"
    "      <div class=\"rf-step\"><span class=\"rf-step-num\">4</span><div class=\"rf-step-title\">${engT('rf_step4_t')}</div><div class=\"rf-step-desc\">${engT('rf_step4_d')}</div></div>\n"
    "    </div>`;\n"
    "  wrap.innerHTML = `\n"
    "    ${rfHero}\n"
    "    ${uploadsHtml}\n"
    "    <div class=\"gmv-engtab-bar\" role=\"tablist\">\n"
    "      ${tabBtn('focus', engT('eng_subtab_focus'))}\n"
    "      ${tabBtn('paliers', engT('eng_subtab_paliers'))}\n"
    "      ${tabBtn('scoreboard', engT('eng_subtab_score'))}\n"
    "    </div>\n"
    "    <div id=\"engPanel\"></div>`;\n"
)

src = go(src, OLD_HEADER, NEW_HEADER, 'engagement panel: Roue de la Fortune hero + steps')


# ---- Add bronze/silver/gold medal chips to per-client paliers card -----
OLD_NEXT_TARGET = (
    "          return `<div style=\"margin-top:8px; padding-top:8px; border-top:1px solid #f1f5f9;\">\n"
    "            <div style=\"display:flex; justify-content:space-between; align-items:baseline; font-size:11.5px; gap:8px; flex-wrap:wrap;\">\n"
    "              <span style=\"color:#64748b;\">${engT('pal_next_target')} : <b style=\"color:#0f172a;\">${engT('pal_lvl', { n: targetP.palier })}</b></span>\n"
    "              <span style=\"color:#64748b; font-size:10.5px;\"><b style=\"color:#0f172a;\">${fmt(cBoth)}</b> / ${fmt(targetP.threshold)} MAD</span>\n"
    "            </div>\n"
    "            <div style=\"height:3px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:5px;\">\n"
    "              <div style=\"height:100%; width:${progPct}%; background:#3b82f6; transition:width .4s;\"></div>\n"
    "            </div>\n"
    "            <div style=\"font-size:10.5px; color:#64748b; margin-top:3px;\">${engT('pal_remaining', { n: fmt(remaining) })}</div>\n"
    "          </div>`;\n"
    "        })()}\n"
)

NEW_NEXT_TARGET = (
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
)

src = go(src, OLD_NEXT_TARGET, NEW_NEXT_TARGET, 'per-client palier: bronze/silver/gold medal chips')


if fails:
    print('FAIL — not writing. ' + str(len(fails)) + ' step(s) failed.')
    sys.exit(2)

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
