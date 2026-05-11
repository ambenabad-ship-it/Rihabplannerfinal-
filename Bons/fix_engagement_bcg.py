# -*- coding: utf-8 -*-
"""
Engagement page — BCG-tier redesign.

Replaces the previous emoji + multi-color KPI cards with a consulting-grade
visual language:

  * Restrained palette — deep navy (#0B2545) + bronze (#B08D57) + neutrals.
  * No emoji. Type and bars only.
  * Sub-tabs become understated underline tabs with a bronze active rule.
  * Personal scoreboard hero: solid navy with a fine bronze top rule, an
    eyebrow, large performance index, "as of <date>", and a single-line
    progress strip.
  * KPI cards: white surface, 1px border, label in tracking-uppercase,
    big tabular number with /denominator, 2px linear progress bar, footer
    with status copy. Achieved cards flip to a green top-rule.
  * Same KPI component reused on the Focus tab so the page reads as one
    deliverable.
  * RTL-aware (uses inset-inline / start-end alignment).

Run:
  python fix_engagement_bcg.py

Idempotent.
"""

import io
import os
import sys


def _find_index():
    if len(sys.argv) > 1:
        return os.path.abspath(sys.argv[1])
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.normpath(os.path.join(
            here, '..', '..', 'Rehab app ( planner) - Copie',
            'rigab_app', 'index.html')),
        os.path.normpath(os.path.join(
            here, '..', 'Rehab app ( planner) - Copie',
            'rigab_app', 'index.html')),
        '/sessions/vibrant-tender-mayer/mnt/Rehab app ( planner) - Copie/rigab_app/index.html',
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    print('Could not find index.html.')
    sys.exit(1)


INDEX_PATH = _find_index()
CSS_BEGIN = '/* === ENGAGEMENT BCG REDESIGN — fix_engagement_bcg.py === */'
CSS_END   = '/* === END ENGAGEMENT BCG REDESIGN === */'


def read_file(path):
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def write_file(path, content):
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)


def replace_once(src, old, new, label, nl='\n'):
    if nl != '\n':
        old = old.replace('\n', nl)
        new = new.replace('\n', nl)
    if new in src and old not in src:
        print('  [skip] ' + label + ' (already applied)')
        return src, False
    if old not in src:
        print('  [FAIL] ' + label + ' (anchor not found)')
        sys.exit(2)
    if src.count(old) != 1:
        print('  [FAIL] ' + label + ' (anchor not unique: '
              + str(src.count(old)) + ' matches)')
        sys.exit(2)
    print('  [ok]   ' + label)
    return src.replace(old, new, 1), True


def strip_block(src, begin, end, indent_chars=2):
    if begin not in src or end not in src:
        return src
    a = src.index(begin)
    b = src.index(end) + len(end)
    e = b
    while e < len(src) and src[e] in ('\n', '\r'):
        e += 1
    s = a
    if indent_chars and s >= indent_chars and src[s-indent_chars:s] == ' ' * indent_chars:
        s -= indent_chars
    while s > 0 and src[s-1] in ('\n', '\r'):
        s -= 1
    return src[:s] + src[e:]


CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  /* Tokens — deep navy, bronze accent, restrained neutrals. */\n'
    '  :root {\n'
    '    --bcg-ink:        #0B2545;\n'
    '    --bcg-ink-2:      #134074;\n'
    '    --bcg-ink-soft:   #6B7280;\n'
    '    --bcg-line:       #E5E7EB;\n'
    '    --bcg-line-soft:  #F1F2F4;\n'
    '    --bcg-surface:    #FFFFFF;\n'
    '    --bcg-surface-2:  #F8F9FA;\n'
    '    --bcg-bronze:     #B08D57;\n'
    '    --bcg-bronze-2:   #D4AF7A;\n'
    '    --bcg-success:    #047857;\n'
    '    --bcg-text:       #111827;\n'
    '  }\n'
    '\n'
    '  /* Sub-tab bar — McKinsey/BCG underline tabs (override fix_gmv_mobile). */\n'
    '  .gmv-engtab-bar {\n'
    '    background: transparent !important;\n'
    '    box-shadow: none !important;\n'
    '    padding: 0 !important;\n'
    '    border-radius: 0 !important;\n'
    '    border-bottom: 1px solid var(--bcg-line);\n'
    '    gap: 0 !important;\n'
    '    margin: 0 0 22px !important;\n'
    '    flex-wrap: nowrap !important;\n'
    '  }\n'
    '  .gmv-engtab {\n'
    '    flex: 1 1 0 !important;\n'
    '    min-width: 0 !important;\n'
    '    background: transparent !important;\n'
    '    color: var(--bcg-ink-soft) !important;\n'
    '    border: 0 !important;\n'
    '    border-radius: 0 !important;\n'
    '    border-bottom: 2px solid transparent !important;\n'
    '    padding: 12px 8px !important;\n'
    '    font-size: 12px !important;\n'
    '    font-weight: 600 !important;\n'
    '    letter-spacing: 0.02em;\n'
    '    box-shadow: none !important;\n'
    '    transition: color .15s, border-color .15s;\n'
    '    margin-bottom: -1px;\n'
    '  }\n'
    '  .gmv-engtab:hover { color: var(--bcg-ink) !important; }\n'
    '  .gmv-engtab.active {\n'
    '    color: var(--bcg-ink) !important;\n'
    '    border-bottom-color: var(--bcg-bronze) !important;\n'
    '  }\n'
    '\n'
    '  /* Page eyebrow / metadata strip. */\n'
    '  .bcg-eyebrow {\n'
    '    font-size: 10px;\n'
    '    font-weight: 600;\n'
    '    letter-spacing: 0.18em;\n'
    '    text-transform: uppercase;\n'
    '    color: var(--bcg-ink-soft);\n'
    '  }\n'
    '\n'
    '  /* Hero — performance index card. */\n'
    '  .bcg-hero {\n'
    '    position: relative;\n'
    '    background: linear-gradient(180deg, var(--bcg-ink) 0%, var(--bcg-ink-2) 100%);\n'
    '    color: #fff;\n'
    '    border-radius: 4px;\n'
    '    padding: 22px 22px 20px;\n'
    '    margin: 0 0 14px;\n'
    '    overflow: hidden;\n'
    '  }\n'
    '  .bcg-hero::before {\n'
    '    content: "";\n'
    '    position: absolute;\n'
    '    inset: 0 0 auto 0;\n'
    '    height: 3px;\n'
    '    background: linear-gradient(90deg, var(--bcg-bronze) 0%, var(--bcg-bronze-2) 50%, var(--bcg-bronze) 100%);\n'
    '  }\n'
    '  .bcg-hero .bcg-eyebrow { color: rgba(255, 255, 255, 0.65); }\n'
    '  .bcg-hero-grid {\n'
    '    display: flex;\n'
    '    align-items: flex-end;\n'
    '    justify-content: space-between;\n'
    '    gap: 18px;\n'
    '    flex-wrap: wrap;\n'
    '    margin-top: 18px;\n'
    '  }\n'
    '  .bcg-hero-id .bcg-hero-name {\n'
    '    font-size: 22px;\n'
    '    font-weight: 700;\n'
    '    letter-spacing: -0.01em;\n'
    '    line-height: 1.1;\n'
    '  }\n'
    '  .bcg-hero-id .bcg-hero-meta {\n'
    '    margin-top: 6px;\n'
    '    font-size: 11px;\n'
    '    color: rgba(255, 255, 255, 0.6);\n'
    '    font-weight: 500;\n'
    '    letter-spacing: 0.02em;\n'
    '  }\n'
    '  .bcg-hero-score {\n'
    '    text-align: end;\n'
    '    min-width: 96px;\n'
    '  }\n'
    '  .bcg-hero-score .bcg-score-num {\n'
    '    font-size: 44px;\n'
    '    font-weight: 800;\n'
    '    letter-spacing: -0.03em;\n'
    '    line-height: 1;\n'
    '    font-variant-numeric: tabular-nums;\n'
    '  }\n'
    '  .bcg-hero-score .bcg-score-label {\n'
    '    margin-top: 6px;\n'
    '    font-size: 9.5px;\n'
    '    letter-spacing: 0.18em;\n'
    '    font-weight: 600;\n'
    '    text-transform: uppercase;\n'
    '    color: rgba(255, 255, 255, 0.7);\n'
    '  }\n'
    '  .bcg-hero-bar {\n'
    '    margin-top: 18px;\n'
    '    height: 3px;\n'
    '    background: rgba(255, 255, 255, 0.16);\n'
    '    overflow: hidden;\n'
    '    border-radius: 0;\n'
    '  }\n'
    '  .bcg-hero-bar > span {\n'
    '    display: block;\n'
    '    height: 100%;\n'
    '    background: var(--bcg-bronze-2);\n'
    '    transition: width 1s cubic-bezier(.2,.7,.3,1);\n'
    '  }\n'
    '  .bcg-hero.is-zero {\n'
    '    background: var(--bcg-surface);\n'
    '    color: var(--bcg-text);\n'
    '    border: 1px solid var(--bcg-line);\n'
    '  }\n'
    '  .bcg-hero.is-zero::before { background: var(--bcg-bronze); }\n'
    '  .bcg-hero.is-zero .bcg-eyebrow { color: var(--bcg-ink-soft); }\n'
    '  .bcg-hero.is-zero .bcg-hero-id .bcg-hero-meta { color: var(--bcg-ink-soft); }\n'
    '  .bcg-hero.is-zero .bcg-hero-score .bcg-score-label { color: var(--bcg-ink-soft); }\n'
    '  .bcg-hero.is-zero .bcg-hero-bar { background: var(--bcg-line-soft); }\n'
    '\n'
    '  /* KPI grid + card. */\n'
    '  .bcg-kpi-grid {\n'
    '    display: grid;\n'
    '    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));\n'
    '    gap: 10px;\n'
    '    margin-bottom: 16px;\n'
    '  }\n'
    '  .bcg-kpi {\n'
    '    position: relative;\n'
    '    background: var(--bcg-surface);\n'
    '    border: 1px solid var(--bcg-line);\n'
    '    border-radius: 4px;\n'
    '    padding: 16px 18px 14px;\n'
    '  }\n'
    '  .bcg-kpi::before {\n'
    '    content: "";\n'
    '    position: absolute;\n'
    '    inset: 0 0 auto 0;\n'
    '    height: 2px;\n'
    '    background: var(--bcg-bronze);\n'
    '    opacity: .85;\n'
    '  }\n'
    '  .bcg-kpi.is-done { border-color: var(--bcg-success); }\n'
    '  .bcg-kpi.is-done::before { background: var(--bcg-success); opacity: 1; }\n'
    '  .bcg-kpi.is-empty::before { background: var(--bcg-line); }\n'
    '  .bcg-kpi-label {\n'
    '    font-size: 9.5px;\n'
    '    font-weight: 600;\n'
    '    letter-spacing: 0.16em;\n'
    '    text-transform: uppercase;\n'
    '    color: var(--bcg-ink-soft);\n'
    '  }\n'
    '  .bcg-kpi-value {\n'
    '    margin-top: 8px;\n'
    '    display: flex;\n'
    '    align-items: baseline;\n'
    '    gap: 6px;\n'
    '    font-variant-numeric: tabular-nums;\n'
    '  }\n'
    '  .bcg-kpi-value .num {\n'
    '    font-size: 30px;\n'
    '    font-weight: 800;\n'
    '    color: var(--bcg-ink);\n'
    '    letter-spacing: -0.02em;\n'
    '    line-height: 1;\n'
    '  }\n'
    '  .bcg-kpi-value .den {\n'
    '    font-size: 13px;\n'
    '    font-weight: 500;\n'
    '    color: #9CA3AF;\n'
    '  }\n'
    '  .bcg-kpi-bar {\n'
    '    margin-top: 12px;\n'
    '    height: 2px;\n'
    '    background: var(--bcg-line-soft);\n'
    '  }\n'
    '  .bcg-kpi-bar > span {\n'
    '    display: block;\n'
    '    height: 100%;\n'
    '    background: var(--bcg-bronze);\n'
    '    transition: width 1s cubic-bezier(.2,.7,.3,1);\n'
    '  }\n'
    '  .bcg-kpi.is-done .bcg-kpi-bar > span { background: var(--bcg-success); }\n'
    '  .bcg-kpi-foot {\n'
    '    margin-top: 10px;\n'
    '    font-size: 11px;\n'
    '    font-weight: 500;\n'
    '    color: var(--bcg-ink-soft);\n'
    '    line-height: 1.4;\n'
    '  }\n'
    '  .bcg-kpi.is-done .bcg-kpi-foot { color: var(--bcg-success); font-weight: 600; }\n'
    '\n'
    '  /* Section header with thin bronze rule above. */\n'
    '  .bcg-section-head {\n'
    '    margin: 18px 0 10px;\n'
    '    padding-top: 14px;\n'
    '    border-top: 1px solid var(--bcg-line);\n'
    '    display: flex;\n'
    '    justify-content: space-between;\n'
    '    align-items: baseline;\n'
    '    gap: 12px;\n'
    '  }\n'
    '  .bcg-section-head .bcg-eyebrow { color: var(--bcg-ink); }\n'
    '\n'
    '  /* Footnote source line — consulting-deck flair. */\n'
    '  .bcg-footnote {\n'
    '    margin-top: 16px;\n'
    '    padding-top: 10px;\n'
    '    border-top: 1px solid var(--bcg-line);\n'
    '    font-size: 10px;\n'
    '    color: var(--bcg-ink-soft);\n'
    '    letter-spacing: 0.04em;\n'
    '    line-height: 1.5;\n'
    '  }\n'
    '\n'
    '  /* RTL polish. */\n'
    '  [dir="rtl"] .bcg-hero-score { text-align: start; }\n'
    '\n'
    '  @media (max-width: 768px) {\n'
    '    .bcg-hero { padding: 20px 18px 18px; }\n'
    '    .bcg-hero-score .bcg-score-num { font-size: 38px; }\n'
    '    .bcg-hero-id .bcg-hero-name { font-size: 19px; }\n'
    '    .bcg-kpi { padding: 14px 16px 12px; }\n'
    '    .bcg-kpi-value .num { font-size: 26px; }\n'
    '    .gmv-engtab { font-size: 11.5px !important; padding: 11px 4px !important; }\n'
    '  }\n'
    + CSS_END
)


# Replace personal-view block (currently the eng-kpi version from
# fix_engagement_design.py) with the BCG version.
OLD_PERSONAL = (
    "    const m1Pct = Math.min(100, Math.round((me.m1Achieved / ENG_MILESTONE_M1) * 100));\n"
    "    const bothPct = Math.min(100, Math.round((me.bothAchieved / ENG_MILESTONE_BOTH) * 100));\n"
    "    const allZero = (me.score === 0 && me.focusHit === 0 && me.m1Achieved === 0 && me.bothAchieved === 0);\n"
    "    // Soft hero when nothing achieved yet — encouraging, not bleak.\n"
    "    const heroHtml = allZero\n"
    "      ? `<div class=\"eng-hero-soft\">\n"
    "          <div style=\"font-size:11px; color:#475569; text-transform:uppercase; letter-spacing:.08em; font-weight:700; margin-bottom:8px;\">${engT('sc_my_perf')} · ${period}</div>\n"
    "          <div style=\"font-size:20px; font-weight:800; color:#0f172a; margin-bottom:6px;\">${gmvEscapeHtmlEng(me.seller)}</div>\n"
    "          <div class=\"eng-hero-emoji\">🚀</div>\n"
    "          <div class=\"eng-hero-title\">${engT('sc_keep')}</div>\n"
    "          <div class=\"eng-hero-sub\">${engT('eng_milestone_m1_hint')}</div>\n"
    "        </div>`\n"
    "      : (() => {\n"
    "          const scoreColor = me.score >= 75 ? '#16a34a' : me.score >= 40 ? '#f59e0b' : '#dc2626';\n"
    "          const moodEmoji = me.score >= 75 ? '🔥' : me.score >= 40 ? '👍' : '💪';\n"
    "          const moodTxt = me.score >= 75 ? engT('sc_great') : me.score >= 40 ? engT('sc_good') : engT('sc_keep');\n"
    "          return `<div style=\"background:linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius:18px; padding:24px 22px; color:#fff; margin-bottom:14px; position:relative; overflow:hidden;\">\n"
    "            <div style=\"position:absolute; top:-30px; inset-inline-end:-30px; width:160px; height:160px; background:radial-gradient(circle, ${scoreColor}40 0%, transparent 70%); border-radius:50%; pointer-events:none;\"></div>\n"
    "            <div style=\"position:relative; display:flex; align-items:center; gap:20px; flex-wrap:wrap;\">\n"
    "              <div style=\"flex-shrink:0;\">${donut(me.score, scoreColor, 120, 12, '')}</div>\n"
    "              <div style=\"flex:1; min-width:160px;\">\n"
    "                <div style=\"font-size:10px; opacity:.7; text-transform:uppercase; letter-spacing:.08em; margin-bottom:4px;\">${engT('sc_my_perf')} · ${period}</div>\n"
    "                <div style=\"font-size:20px; font-weight:800;\">${gmvEscapeHtmlEng(me.seller)}</div>\n"
    "                <div style=\"margin-top:8px; font-size:13px; opacity:.95;\">${moodEmoji} <b>${moodTxt}</b></div>\n"
    "                <div style=\"margin-top:4px; font-size:12px; opacity:.7;\">${engT('sc_overall')} : <b style=\"color:${scoreColor};\">${me.score}%</b></div>\n"
    "              </div>\n"
    "            </div>\n"
    "          </div>`;\n"
    "        })();\n"
    "    // KPI card factory — accent color drives the side stripe + icon halo.\n"
    "    // `done` flips the card to a green-tinted achieved state.\n"
    "    const kpi = (opts) => {\n"
    "      const accent = opts.accent || '#3b82f6';\n"
    "      const soft = opts.softBg || '#eff6ff';\n"
    "      const done = !!opts.done;\n"
    "      const empty = !!opts.empty;\n"
    "      const cls = 'eng-kpi' + (done ? ' is-done' : '') + (empty ? ' is-empty' : '');\n"
    "      const total = (opts.total != null) ? '<span class=\"eng-kpi-total\"> / ' + opts.total + '</span>' : '';\n"
    "      const hintCol = done ? '#16a34a' : '#64748b';\n"
    "      return `<div class=\"${cls}\" style=\"--kpi-accent:${accent}; --kpi-accent-soft:${soft};\">\n"
    "        <div class=\"eng-kpi-row\">\n"
    "          <div class=\"eng-kpi-icon\">${opts.icon || ''}</div>\n"
    "          <div class=\"eng-kpi-body\">\n"
    "            <div class=\"eng-kpi-label\">${opts.label}</div>\n"
    "            <div class=\"eng-kpi-value\">${opts.value}${total}</div>\n"
    "            <div class=\"eng-kpi-hint\" style=\"color:${hintCol};\">${opts.hint || ''}</div>\n"
    "          </div>\n"
    "        </div>\n"
    "      </div>`;\n"
    "    };\n"
    "    // Inline SVG icons for the four KPIs.\n"
    "    const ico = {\n"
    "      target:   '<svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"12\" cy=\"12\" r=\"9\"/><circle cx=\"12\" cy=\"12\" r=\"5\"/><circle cx=\"12\" cy=\"12\" r=\"1.5\" fill=\"currentColor\"/></svg>',\n"
    "      cal1:     '<svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"5\" width=\"18\" height=\"16\" rx=\"2\"/><path d=\"M3 10h18M8 3v4M16 3v4\"/><text x=\"12\" y=\"18\" text-anchor=\"middle\" font-size=\"7\" font-weight=\"800\" fill=\"currentColor\" stroke=\"none\">5</text></svg>',\n"
    "      cal2:     '<svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"5\" width=\"18\" height=\"16\" rx=\"2\"/><path d=\"M3 10h18M8 3v4M16 3v4\"/><text x=\"12\" y=\"18\" text-anchor=\"middle\" font-size=\"6.5\" font-weight=\"800\" fill=\"currentColor\" stroke=\"none\">10</text></svg>',\n"
    "      crown:    '<svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 8l4 4 5-7 5 7 4-4-2 11H5z\"/></svg>'\n"
    "    };\n"
    "    panel.innerHTML = heroHtml + `\n"
    "      <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-bottom:14px;\">\n"
    "        ${kpi({\n"
    "          accent: '#3b82f6', softBg: '#dbeafe',\n"
    "          icon: ico.target,\n"
    "          label: engT('sc_focus_score'),\n"
    "          value: me.focusHit,\n"
    "          total: me.focusTotal,\n"
    "          hint: engT('sc_committed') + ' : ' + me.focusTotal,\n"
    "          done: me.focusTotal > 0 && me.focusHit === me.focusTotal,\n"
    "          empty: me.focusTotal === 0\n"
    "        })}\n"
    "        ${kpi({\n"
    "          accent: '#0ea5e9', softBg: '#e0f2fe',\n"
    "          icon: ico.cal1,\n"
    "          label: engT('eng_milestone_m1'),\n"
    "          value: me.m1Achieved,\n"
    "          total: ENG_MILESTONE_M1,\n"
    "          hint: me.m1Done ? engT('eng_milestone_done') : engT('eng_milestone_m1_hint'),\n"
    "          done: me.m1Done\n"
    "        })}\n"
    "        ${kpi({\n"
    "          accent: '#a855f7', softBg: '#f3e8ff',\n"
    "          icon: ico.cal2,\n"
    "          label: engT('eng_milestone_both'),\n"
    "          value: me.bothAchieved,\n"
    "          total: ENG_MILESTONE_BOTH,\n"
    "          hint: me.bothDone ? engT('eng_milestone_done') : engT('eng_milestone_both_hint'),\n"
    "          done: me.bothDone\n"
    "        })}\n"
    "        ${kpi({\n"
    "          accent: '#f59e0b', softBg: '#fef3c7',\n"
    "          icon: ico.crown,\n"
    "          label: engT('sc_palier_score'),\n"
    "          value: me.palierHit,\n"
    "          total: me.palierTotal,\n"
    "          hint: engT('sc_clients_paliers'),\n"
    "          done: me.palierTotal > 0 && me.palierHit === me.palierTotal,\n"
    "          empty: me.palierTotal === 0\n"
    "        })}\n"
    "      </div>`;\n"
    "    return;\n"
)


NEW_PERSONAL = (
    "    const m1Pct   = Math.min(100, Math.round((me.m1Achieved   / ENG_MILESTONE_M1)   * 100));\n"
    "    const bothPct = Math.min(100, Math.round((me.bothAchieved / ENG_MILESTONE_BOTH) * 100));\n"
    "    const focusPct = me.focusTotal ? Math.round((me.focusHit / me.focusTotal) * 100) : 0;\n"
    "    const palPct   = me.palierTotal ? Math.round((me.palierHit / me.palierTotal) * 100) : 0;\n"
    "    const isZero  = (me.score === 0 && me.focusHit === 0 && me.m1Achieved === 0 && me.bothAchieved === 0 && me.palierHit === 0);\n"
    "    // Localized 'as of <date>' line — consulting deliverables footnote the data freshness.\n"
    "    const asOfLocale = engLang() === 'ar' ? 'ar-EG' : (engLang() === 'fr' ? 'fr-FR' : 'en-GB');\n"
    "    const asOfDate = new Date().toLocaleDateString(asOfLocale, { day: '2-digit', month: 'short', year: 'numeric' });\n"
    "    const asOfPrefix = engLang() === 'ar' ? 'بتاريخ' : (engLang() === 'fr' ? 'au' : 'as of');\n"
    "    // Hero card.\n"
    "    const heroHtml = `\n"
    "      <header class=\"bcg-hero${isZero ? ' is-zero' : ''}\">\n"
    "        <div class=\"bcg-eyebrow\">${engT('eng_campaign')}</div>\n"
    "        <div class=\"bcg-hero-grid\">\n"
    "          <div class=\"bcg-hero-id\">\n"
    "            <div class=\"bcg-hero-name\">${gmvEscapeHtmlEng(me.seller)}</div>\n"
    "            <div class=\"bcg-hero-meta\">${asOfPrefix} ${asOfDate} · ${period}</div>\n"
    "          </div>\n"
    "          <div class=\"bcg-hero-score\">\n"
    "            <div class=\"bcg-score-num\">${me.score}<span style=\"font-size:.55em; font-weight:700;\">%</span></div>\n"
    "            <div class=\"bcg-score-label\">${engT('sc_overall')}</div>\n"
    "          </div>\n"
    "        </div>\n"
    "        <div class=\"bcg-hero-bar\"><span style=\"width:${me.score}%;\"></span></div>\n"
    "      </header>`;\n"
    "    // KPI card factory — pure type + linear progress, no donuts, no emoji.\n"
    "    const kpi = (opts) => {\n"
    "      const done = !!opts.done;\n"
    "      const empty = !!opts.empty;\n"
    "      const cls = 'bcg-kpi' + (done ? ' is-done' : '') + (empty ? ' is-empty' : '');\n"
    "      const den = (opts.total != null) ? '<span class=\"den\">/ ' + opts.total + '</span>' : '';\n"
    "      const pct = Math.max(0, Math.min(100, opts.pct || 0));\n"
    "      return `<article class=\"${cls}\">\n"
    "        <div class=\"bcg-kpi-label\">${opts.label}</div>\n"
    "        <div class=\"bcg-kpi-value\"><span class=\"num\">${opts.value}</span>${den}</div>\n"
    "        <div class=\"bcg-kpi-bar\"><span style=\"width:${pct}%;\"></span></div>\n"
    "        <div class=\"bcg-kpi-foot\">${opts.hint || ''}</div>\n"
    "      </article>`;\n"
    "    };\n"
    "    panel.innerHTML = heroHtml + `\n"
    "      <div class=\"bcg-kpi-grid\">\n"
    "        ${kpi({\n"
    "          label: engT('sc_focus_score'),\n"
    "          value: me.focusHit,\n"
    "          total: me.focusTotal,\n"
    "          pct: focusPct,\n"
    "          hint: engT('sc_committed') + ' · ' + me.focusTotal,\n"
    "          done: me.focusTotal > 0 && me.focusHit === me.focusTotal,\n"
    "          empty: me.focusTotal === 0\n"
    "        })}\n"
    "        ${kpi({\n"
    "          label: engT('eng_milestone_m1'),\n"
    "          value: me.m1Achieved,\n"
    "          total: ENG_MILESTONE_M1,\n"
    "          pct: m1Pct,\n"
    "          hint: me.m1Done ? engT('eng_milestone_done') : engT('eng_milestone_m1_hint'),\n"
    "          done: me.m1Done\n"
    "        })}\n"
    "        ${kpi({\n"
    "          label: engT('eng_milestone_both'),\n"
    "          value: me.bothAchieved,\n"
    "          total: ENG_MILESTONE_BOTH,\n"
    "          pct: bothPct,\n"
    "          hint: me.bothDone ? engT('eng_milestone_done') : engT('eng_milestone_both_hint'),\n"
    "          done: me.bothDone\n"
    "        })}\n"
    "        ${kpi({\n"
    "          label: engT('sc_palier_score'),\n"
    "          value: me.palierHit,\n"
    "          total: me.palierTotal,\n"
    "          pct: palPct,\n"
    "          hint: engT('sc_clients_paliers'),\n"
    "          done: me.palierTotal > 0 && me.palierHit === me.palierTotal,\n"
    "          empty: me.palierTotal === 0\n"
    "        })}\n"
    "      </div>\n"
    "      <div class=\"bcg-footnote\">${engT('eng_campaign_rule')}</div>`;\n"
    "    return;\n"
)


# Replace the focus tab's 4-card header KPIs to use the same .bcg-kpi
# component so the page reads as one consistent deliverable.
OLD_FOCUS_HEADER = (
    "  const headerHtml = `\n"
    "    <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-bottom:16px;\">\n"
    "      <div style=\"padding:18px 20px; background:linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color:#fff; border-radius:14px;\">\n"
    "        <div style=\"font-size:11px; opacity:.7; text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px;\">${engT('eng_period_label')} · ${engT('eng_seller_label')}</div>\n"
    "        <div style=\"font-size:18px; font-weight:700; line-height:1.2;\">${period}</div>\n"
    "        <div style=\"font-size:13px; opacity:.85; margin-top:2px;\">${gmvEscapeHtmlEng(seller)}</div>\n"
    "      </div>\n"
    "      <div style=\"padding:18px 20px; background:#fff; border:1px solid #e2e8f0; border-radius:14px;\">\n"
    "        <div style=\"font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px;\">${engT('eng_committed')}</div>\n"
    "        <div style=\"font-size:28px; font-weight:700; color:${minOk ? '#16a34a' : '#dc2626'};\">${selectedCodes.length}<span style=\"font-size:14px; color:#94a3b8; font-weight:500;\"> / ${ENG_MIN_PRODUCTS} ${engT('eng_min_short')}</span></div>\n"
    "        <div style=\"font-size:11px; color:${minOk ? '#16a34a' : '#dc2626'}; margin-top:4px;\">${minOk ? engT('eng_min_ok') : engT('eng_select_more', { n: ENG_MIN_PRODUCTS - selectedCodes.length })}</div>\n"
    "      </div>\n"
    "      <div style=\"padding:18px 20px; background:#fff; border:1px solid #e2e8f0; border-radius:14px;\">\n"
    "        <div style=\"font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px;\">${engT('eng_milestone_m1')}</div>\n"
    "        <div style=\"font-size:28px; font-weight:700; color:${m1Done ? '#16a34a' : '#0369a1'};\">${m1Stats.achieved}<span style=\"font-size:14px; color:#94a3b8; font-weight:500;\"> / ${ENG_MILESTONE_M1}</span></div>\n"
    "        <div style=\"height:6px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:8px;\">\n"
    "          <div style=\"height:100%; width:${m1Pct}%; background:${m1Done ? '#16a34a' : '#0369a1'}; transition:width .4s;\"></div>\n"
    "        </div>\n"
    "        <div style=\"font-size:11px; color:${m1Done ? '#16a34a' : '#64748b'}; margin-top:6px; font-weight:600;\">${m1Done ? engT('eng_milestone_done') : engT('eng_milestone_m1_hint')}</div>\n"
    "      </div>\n"
    "      <div style=\"padding:18px 20px; background:#fff; border:1px solid #e2e8f0; border-radius:14px;\">\n"
    "        <div style=\"font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px;\">${engT('eng_milestone_both')}</div>\n"
    "        <div style=\"font-size:28px; font-weight:700; color:${bothDone ? '#16a34a' : '#7c3aed'};\">${both.achieved}<span style=\"font-size:14px; color:#94a3b8; font-weight:500;\"> / ${ENG_MILESTONE_BOTH}</span></div>\n"
    "        <div style=\"height:6px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:8px;\">\n"
    "          <div style=\"height:100%; width:${bothPct}%; background:${bothDone ? '#16a34a' : '#7c3aed'}; transition:width .4s;\"></div>\n"
    "        </div>\n"
    "        <div style=\"font-size:11px; color:${bothDone ? '#16a34a' : '#64748b'}; margin-top:6px; font-weight:600;\">${bothDone ? engT('eng_milestone_done') : engT('eng_milestone_both_hint')}</div>\n"
    "      </div>\n"
    "    </div>`;\n"
)

NEW_FOCUS_HEADER = (
    "  // BCG-style header: one navy hero card + 3 KPI cards in a grid.\n"
    "  const _focusFmt = n => Math.round(n || 0).toLocaleString('en-US');\n"
    "  const _asOfLocale = engLang() === 'ar' ? 'ar-EG' : (engLang() === 'fr' ? 'fr-FR' : 'en-GB');\n"
    "  const _asOfDate = new Date().toLocaleDateString(_asOfLocale, { day: '2-digit', month: 'short', year: 'numeric' });\n"
    "  const _asOfPrefix = engLang() === 'ar' ? 'بتاريخ' : (engLang() === 'fr' ? 'au' : 'as of');\n"
    "  const _commitPct = Math.min(100, Math.round((selectedCodes.length / ENG_MIN_PRODUCTS) * 100));\n"
    "  const _bcgKpi = (opts) => {\n"
    "    const done  = !!opts.done;\n"
    "    const empty = !!opts.empty;\n"
    "    const cls = 'bcg-kpi' + (done ? ' is-done' : '') + (empty ? ' is-empty' : '');\n"
    "    const den = (opts.total != null) ? '<span class=\"den\">/ ' + opts.total + '</span>' : '';\n"
    "    const pct = Math.max(0, Math.min(100, opts.pct || 0));\n"
    "    return `<article class=\"${cls}\">\n"
    "      <div class=\"bcg-kpi-label\">${opts.label}</div>\n"
    "      <div class=\"bcg-kpi-value\"><span class=\"num\">${opts.value}</span>${den}</div>\n"
    "      <div class=\"bcg-kpi-bar\"><span style=\"width:${pct}%;\"></span></div>\n"
    "      <div class=\"bcg-kpi-foot\">${opts.hint || ''}</div>\n"
    "    </article>`;\n"
    "  };\n"
    "  const headerHtml = `\n"
    "    <header class=\"bcg-hero\">\n"
    "      <div class=\"bcg-eyebrow\">${engT('eng_campaign')}</div>\n"
    "      <div class=\"bcg-hero-grid\">\n"
    "        <div class=\"bcg-hero-id\">\n"
    "          <div class=\"bcg-hero-name\">${gmvEscapeHtmlEng(seller)}</div>\n"
    "          <div class=\"bcg-hero-meta\">${_asOfPrefix} ${_asOfDate} · ${period}</div>\n"
    "        </div>\n"
    "        <div class=\"bcg-hero-score\">\n"
    "          <div class=\"bcg-score-num\">${_focusFmt(total)}</div>\n"
    "          <div class=\"bcg-score-label\">${engT('eng_total_gmv')} (MAD)</div>\n"
    "        </div>\n"
    "      </div>\n"
    "      <div class=\"bcg-hero-bar\"><span style=\"width:${_commitPct}%;\"></span></div>\n"
    "    </header>\n"
    "    <div class=\"bcg-kpi-grid\">\n"
    "      ${_bcgKpi({\n"
    "        label: engT('eng_committed'),\n"
    "        value: selectedCodes.length,\n"
    "        total: ENG_MIN_PRODUCTS,\n"
    "        pct: _commitPct,\n"
    "        hint: minOk ? engT('eng_min_ok') : engT('eng_select_more', { n: ENG_MIN_PRODUCTS - selectedCodes.length }),\n"
    "        done: minOk\n"
    "      })}\n"
    "      ${_bcgKpi({\n"
    "        label: engT('eng_milestone_m1'),\n"
    "        value: m1Stats.achieved,\n"
    "        total: ENG_MILESTONE_M1,\n"
    "        pct: m1Pct,\n"
    "        hint: m1Done ? engT('eng_milestone_done') : engT('eng_milestone_m1_hint'),\n"
    "        done: m1Done\n"
    "      })}\n"
    "      ${_bcgKpi({\n"
    "        label: engT('eng_milestone_both'),\n"
    "        value: both.achieved,\n"
    "        total: ENG_MILESTONE_BOTH,\n"
    "        pct: bothPct,\n"
    "        hint: bothDone ? engT('eng_milestone_done') : engT('eng_milestone_both_hint'),\n"
    "        done: bothDone\n"
    "      })}\n"
    "    </div>`;\n"
)


def main():
    print('Patching: ' + INDEX_PATH)
    src = read_file(INDEX_PATH)
    nl = '\r\n' if '\r\n' in src else '\n'

    src = strip_block(src, CSS_BEGIN, CSS_END)
    css_anchor = nl + '  /* RTL fine-tuning for Arabic */' + nl
    if css_anchor not in src:
        print('  [FAIL] CSS anchor not found')
        sys.exit(2)
    src = src.replace(css_anchor, nl + '  ' + CSS_BLOCK.replace('\n', nl) + nl + css_anchor, 1)
    print('  [ok]   injected BCG CSS')

    src, _ = replace_once(src, OLD_PERSONAL, NEW_PERSONAL,
                          'scoreboard personal view -> BCG hero + .bcg-kpi grid', nl)

    src, _ = replace_once(src, OLD_FOCUS_HEADER, NEW_FOCUS_HEADER,
                          'focus tab header -> BCG hero + .bcg-kpi grid', nl)

    write_file(INDEX_PATH, src)
    print('Done.')


if __name__ == '__main__':
    main()
