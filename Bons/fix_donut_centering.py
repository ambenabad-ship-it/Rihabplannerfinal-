# -*- coding: utf-8 -*-
"""
Center the donut percentage text properly + restore the original
donut-in-card layout the user said they liked.

Two small fixes:
  1. The donut SVG used `y="48%"` for the percentage label, which sits
     the text BASELINE near center — leaving the glyph visually above
     the geometric centre. Switch to `y="50%"` with
     `dominant-baseline="central"` so the glyph itself centres.
  2. The personal scoreboard view was rewritten by fix_engagement_design.py
     to use icon halos instead of donuts inside the KPI cards. Restore
     the original donut-card layout (gradient hero + 4 white cards each
     with a 64px donut + label + count on its own row).

Run:
  python fix_donut_centering.py

Idempotent. Re-running is safe.
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


# ---- Fix 1: Donut SVG text centering -----------------------------------
OLD_DONUT_TEXT = (
    '        <text x="50%" y="48%" text-anchor="middle" font-size="${Math.round(size*0.22)}" font-weight="700" fill="#0f172a">${pct}%</text>\n'
    '        ${label ? `<text x="50%" y="68%" text-anchor="middle" font-size="${Math.round(size*0.09)}" fill="#64748b">${label}</text>` : \'\'}\n'
)
NEW_DONUT_TEXT = (
    '        <text x="50%" y="50%" text-anchor="middle" dominant-baseline="central" font-size="${Math.round(size*0.22)}" font-weight="700" fill="#0f172a">${pct}%</text>\n'
    '        ${label ? `<text x="50%" y="78%" text-anchor="middle" dominant-baseline="central" font-size="${Math.round(size*0.09)}" fill="#64748b">${label}</text>` : \'\'}\n'
)


# ---- Fix 2: Restore donut-in-card personal scoreboard layout ----------
CURRENT_PERSONAL = (
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


# This is the original donut-in-card design — exactly what the screenshot shows.
ORIGINAL_PERSONAL = (
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
    "        <div style=\"position:relative; display:flex; align-items:center; gap:24px; flex-wrap:wrap; justify-content:center;\">\n"
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
    "            <div style=\"flex-shrink:0; display:flex; align-items:center; justify-content:center;\">${donut(me.focusScorePct, '#3b82f6', 64, 8, '')}</div>\n"
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
    "            <div style=\"flex-shrink:0; display:flex; align-items:center; justify-content:center;\">${donut(m1Pct, m1Color, 64, 8, '')}</div>\n"
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
    "            <div style=\"flex-shrink:0; display:flex; align-items:center; justify-content:center;\">${donut(bothPct, bothColor, 64, 8, '')}</div>\n"
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
    "            <div style=\"flex-shrink:0; display:flex; align-items:center; justify-content:center;\">${donut(me.palierScorePct, '#a855f7', 64, 8, '')}</div>\n"
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


def main():
    print('Patching: ' + INDEX_PATH)
    src = read_file(INDEX_PATH)
    nl = '\r\n' if '\r\n' in src else '\n'

    # Donut helper text centring.
    src, _ = replace_once(src, OLD_DONUT_TEXT, NEW_DONUT_TEXT,
                          'donut SVG text uses dominant-baseline:central + y=50%', nl)

    # Restore donut-in-card personal scoreboard.
    src, _ = replace_once(src, CURRENT_PERSONAL, ORIGINAL_PERSONAL,
                          'restored original donut-in-card scoreboard', nl)

    write_file(INDEX_PATH, src)
    print('Done.')


if __name__ == '__main__':
    main()
