# -*- coding: utf-8 -*-
"""
Engagement page mobile redesign.

Goals (from the audit screenshot):
  1. Top sub-tab bar overlaps the hamburger button on mobile.
  2. The 3-tab strip wraps to 2 rows because of flex:1 1 calc(50% - 4px),
     leaving the active tab orphaned on row 2.
  3. The single-tab #gmvPageBar (sellers only see Engagement) takes the
     full width and looks like a banner. Hide it for sellers; the
     sub-tabs become the page header.
  4. Empty state for the personal scoreboard is too dark (gradient hero
     with redundant 0%/0%) when the seller has no achievements yet.
  5. The 4 KPI cards look interchangeable. Differentiate them with
     accent colors + icons.

Run:
  python fix_engagement_design.py

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
CSS_BEGIN = '/* === ENGAGEMENT REDESIGN — fix_engagement_design.py === */'
CSS_END   = '/* === END ENGAGEMENT REDESIGN === */'


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
    '  /* Sub-tabs: 3 equal columns on one row, no wrap. (#2) */\n'
    '  .gmv-engtab-bar {\n'
    '    flex-wrap: nowrap !important;\n'
    '  }\n'
    '  .gmv-engtab {\n'
    '    flex: 1 1 0 !important;\n'
    '    min-width: 0 !important;\n'
    '  }\n'
    '\n'
    '  /* Sellers see only Engagement in the main page bar — hide it.\n'
    '     The body class is added by JS in gmvRenderPageBar. (#3) */\n'
    '  body.gmv-seller-only .gmv-pagebar { display: none !important; }\n'
    '\n'
    '  @media (max-width: 768px) {\n'
    '    /* Give the engagement page a top safe-area on phones so the\n'
    '       hamburger never sits over the sub-tab strip. (#1) */\n'
    '    body.gmv-seller-only #gmvResultsWrap { padding-top: 12px; }\n'
    '    .gmv-engtab { font-size: 11.5px; padding: 9px 6px; }\n'
    '  }\n'
    '\n'
    '  /* KPI cards: distinct accent stripes + soft icon badge. (#5) */\n'
    '  .eng-kpi {\n'
    '    background: #fff;\n'
    '    border: 1px solid #e2e8f0;\n'
    '    border-radius: 14px;\n'
    '    padding: 16px 18px;\n'
    '    position: relative;\n'
    '    overflow: hidden;\n'
    '  }\n'
    '  .eng-kpi::before {\n'
    '    content: "";\n'
    '    position: absolute;\n'
    '    inset: 0 auto 0 0;\n'
    '    width: 4px;\n'
    '    background: var(--kpi-accent, #94a3b8);\n'
    '  }\n'
    '  [dir="rtl"] .eng-kpi::before { inset: 0 0 0 auto; }\n'
    '  .eng-kpi.is-empty { background: #f8fafc; }\n'
    '  .eng-kpi-row { display: flex; align-items: center; gap: 14px; }\n'
    '  .eng-kpi-row > .eng-kpi-icon {\n'
    '    flex-shrink: 0;\n'
    '    width: 64px; height: 64px; border-radius: 50%;\n'
    '    display: flex; align-items: center; justify-content: center;\n'
    '    background: var(--kpi-accent-soft, #f1f5f9);\n'
    '    color: var(--kpi-accent, #475569);\n'
    '  }\n'
    '  .eng-kpi-body { flex: 1; min-width: 0; }\n'
    '  .eng-kpi-label {\n'
    '    font-size: 11px; color: #64748b;\n'
    '    text-transform: uppercase; letter-spacing: .05em; font-weight: 600;\n'
    '  }\n'
    '  .eng-kpi-value {\n'
    '    font-size: 22px; font-weight: 800; color: #0f172a;\n'
    '    margin-top: 2px; line-height: 1.1;\n'
    '    font-variant-numeric: tabular-nums;\n'
    '  }\n'
    '  .eng-kpi-value .eng-kpi-total {\n'
    '    font-size: 14px; color: #94a3b8; font-weight: 500;\n'
    '  }\n'
    '  .eng-kpi-hint { font-size: 11.5px; color: #64748b; margin-top: 4px; }\n'
    '  .eng-kpi.is-done { background: linear-gradient(135deg, #f0fdf4 0%, #fff 60%); border-color: #bbf7d0; }\n'
    '  .eng-kpi.is-done .eng-kpi-hint { color: #16a34a; font-weight: 600; }\n'
    '\n'
    '  /* Soft hero variant (when seller has 0 achievements). */\n'
    '  .eng-hero-soft {\n'
    '    background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);\n'
    '    border: 1px solid #c7d2fe;\n'
    '    border-radius: 16px;\n'
    '    padding: 20px;\n'
    '    margin-bottom: 14px;\n'
    '    text-align: center;\n'
    '  }\n'
    '  .eng-hero-soft .eng-hero-emoji { font-size: 36px; margin-bottom: 6px; }\n'
    '  .eng-hero-soft .eng-hero-title { font-size: 16px; font-weight: 700; color: #312e81; }\n'
    '  .eng-hero-soft .eng-hero-sub { font-size: 12.5px; color: #4338ca; margin-top: 4px; line-height: 1.5; }\n'
    + CSS_END
)


# ---- Replacement #1: scoreboard personal view (the dark gradient hero +\n'
# 4 identical-looking white KPI cards) -> soft empty state for 0% +\n'
# distinctly-styled KPI cards using .eng-kpi.\n'
OLD_PERSONAL = (
    "    const scoreColor = me.score >= 75 ? '#16a34a' : me.score >= 40 ? '#f59e0b' : '#dc2626';\n"
    "    const moodEmoji = me.score >= 75 ? '🔥' : me.score >= 40 ? '👍' : '💪';\n"
    "    const moodTxt = me.score >= 75 ? engT('sc_great') : me.score >= 40 ? engT('sc_good') : engT('sc_keep');\n"
    "    const m1Color = me.m1Done ? '#16a34a' : '#3b82f6';\n"
    "    const bothColor = me.bothDone ? '#16a34a' : '#a855f7';\n"
    "    const m1Pct = Math.min(100, Math.round((me.m1Achieved / ENG_MILESTONE_M1) * 100));\n"
    "    const bothPct = Math.min(100, Math.round((me.bothAchieved / ENG_MILESTONE_BOTH) * 100));\n"
    "    panel.innerHTML = `\n"
    "      <div style=\"background:linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius:18px; padding:28px 24px; color:#fff; margin-bottom:14px; position:relative; overflow:hidden;\">\n"
    "        <div style=\"position:absolute; top:-30px; right:-30px; width:160px; height:160px; background:radial-gradient(circle, ${scoreColor}40 0%, transparent 70%); border-radius:50%;\"></div>\n"
    "        <div style=\"position:relative; display:flex; align-items:center; gap:24px; flex-wrap:wrap;\">\n"
    "          <div style=\"flex-shrink:0;\">${donut(me.score, scoreColor, 140, 14, '')}</div>\n"
    "          <div style=\"flex:1; min-width:200px;\">\n"
    "            <div style=\"font-size:11px; opacity:.7; text-transform:uppercase; letter-spacing:.08em; margin-bottom:6px;\">${engT('sc_my_perf')} · ${period}</div>\n"
    "            <div style=\"font-size:24px; font-weight:700;\">${gmvEscapeHtmlEng(me.seller)}</div>\n"
    "            <div style=\"margin-top:10px; font-size:14px; opacity:.9;\">${moodEmoji} <b>${moodTxt}</b></div>\n"
    "            <div style=\"margin-top:6px; font-size:12px; opacity:.7;\">${engT('sc_overall')} : <b style=\"color:${scoreColor};\">${me.score}%</b></div>\n"
    "          </div>\n"
    "        </div>\n"
    "      </div>\n"
    "\n"
    "      <div style=\"display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-bottom:14px;\">\n"
    "        <div style=\"background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:18px;\">\n"
    "          <div style=\"display:flex; align-items:center; gap:14px;\">\n"
    "            ${donut(me.focusScorePct, '#3b82f6', 64, 8, '')}\n"
    "            <div style=\"flex:1; min-width:0;\">\n"
    "              <div style=\"font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.05em;\">${engT('sc_focus_score')}</div>\n"
    "              <div style=\"font-size:20px; font-weight:700; color:#0f172a; margin-top:2px;\">${me.focusHit}<span style=\"font-size:14px; color:#94a3b8; font-weight:500;\"> / ${me.focusTotal}</span></div>\n"
    "              <div style=\"font-size:11px; color:#64748b; margin-top:2px;\">${engT('sc_committed')} : ${me.focusTotal} · ${engT('sc_reached')} : ${me.focusHit}</div>\n"
    "            </div>\n"
    "          </div>\n"
    "        </div>\n"
    "\n"
    "        <div style=\"background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:18px;\">\n"
    "          <div style=\"display:flex; align-items:center; gap:14px;\">\n"
    "            ${donut(m1Pct, m1Color, 64, 8, '')}\n"
    "            <div style=\"flex:1; min-width:0;\">\n"
    "              <div style=\"font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.05em;\">${engT('eng_milestone_m1')}</div>\n"
    "              <div style=\"font-size:20px; font-weight:700; color:#0f172a; margin-top:2px;\">${me.m1Achieved}<span style=\"font-size:14px; color:#94a3b8; font-weight:500;\"> / ${ENG_MILESTONE_M1}</span></div>\n"
    "              <div style=\"font-size:11px; color:${me.m1Done ? '#16a34a' : '#64748b'}; margin-top:2px; font-weight:600;\">${me.m1Done ? engT('eng_milestone_done') : engT('eng_milestone_m1_hint')}</div>\n"
    "            </div>\n"
    "          </div>\n"
    "        </div>\n"
    "\n"
    "        <div style=\"background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:18px;\">\n"
    "          <div style=\"display:flex; align-items:center; gap:14px;\">\n"
    "            ${donut(bothPct, bothColor, 64, 8, '')}\n"
    "            <div style=\"flex:1; min-width:0;\">\n"
    "              <div style=\"font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.05em;\">${engT('eng_milestone_both')}</div>\n"
    "              <div style=\"font-size:20px; font-weight:700; color:#0f172a; margin-top:2px;\">${me.bothAchieved}<span style=\"font-size:14px; color:#94a3b8; font-weight:500;\"> / ${ENG_MILESTONE_BOTH}</span></div>\n"
    "              <div style=\"font-size:11px; color:${me.bothDone ? '#16a34a' : '#64748b'}; margin-top:2px; font-weight:600;\">${me.bothDone ? engT('eng_milestone_done') : engT('eng_milestone_both_hint')}</div>\n"
    "            </div>\n"
    "          </div>\n"
    "        </div>\n"
    "\n"
    "        <div style=\"background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:18px;\">\n"
    "          <div style=\"display:flex; align-items:center; gap:14px;\">\n"
    "            ${donut(me.palierScorePct, '#a855f7', 64, 8, '')}\n"
    "            <div style=\"flex:1; min-width:0;\">\n"
    "              <div style=\"font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:.05em;\">${engT('sc_palier_score')}</div>\n"
    "              <div style=\"font-size:20px; font-weight:700; color:#0f172a; margin-top:2px;\">${me.palierHit}<span style=\"font-size:14px; color:#94a3b8; font-weight:500;\"> / ${me.palierTotal}</span></div>\n"
    "              <div style=\"font-size:11px; color:#64748b; margin-top:2px;\">${engT('sc_clients_paliers')}</div>\n"
    "            </div>\n"
    "          </div>\n"
    "        </div>\n"
    "      </div>`;\n"
    "    return;\n"
)


NEW_PERSONAL = (
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


# Replacement #2: hide the page bar for sellers via body class.
OLD_PAGEBAR = (
    "  // Sellers only see Engagement inside GMV Tracker.\n"
    "  const isSeller = (typeof gmvIsSeller === 'function') && gmvIsSeller();\n"
    "  if (isSeller) gmv.activePage = 'engagement';\n"
)
NEW_PAGEBAR = (
    "  // Sellers only see Engagement inside GMV Tracker.\n"
    "  const isSeller = (typeof gmvIsSeller === 'function') && gmvIsSeller();\n"
    "  if (isSeller) gmv.activePage = 'engagement';\n"
    "  // Hide the main page-bar entirely for sellers (only one tab — looks\n"
    "  // like a banner). The body class flips a CSS rule injected by\n"
    "  // fix_engagement_design.py.\n"
    "  try { document.body.classList.toggle('gmv-seller-only', isSeller); } catch (_) {}\n"
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
    print('  [ok]   injected CSS')

    src, _ = replace_once(src, OLD_PAGEBAR, NEW_PAGEBAR,
                          'sellers: hide #gmvPageBar via body class', nl)

    src, _ = replace_once(src, OLD_PERSONAL, NEW_PERSONAL,
                          'scoreboard personal view: soft hero + .eng-kpi cards', nl)

    write_file(INDEX_PATH, src)
    print('Done.')


if __name__ == '__main__':
    main()
