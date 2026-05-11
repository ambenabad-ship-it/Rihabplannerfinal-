# -*- coding: utf-8 -*-
"""
Revert fix_engagement_bcg.py.

Restores the previous engagement design (donuts + colored side-stripes from
fix_engagement_design.py) by:
  * Removing the BCG CSS block.
  * Swapping the scoreboard personal view back to the .eng-kpi version.
  * Swapping the focus tab header back to the original gradient + 4-card
    version.

Run:
  python revert_engagement_bcg.py

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
        return src, False
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
    return src[:s] + src[e:], True


# ---- The "BCG" block we want to remove from the personal view --------
BCG_PERSONAL = (
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


# Restore the eng-kpi version that fix_engagement_design.py installed.
PREVIOUS_PERSONAL = (
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


# ---- Focus tab header — restore the gradient + 4 KPI card version ----
BCG_FOCUS_HEADER = (
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


PREVIOUS_FOCUS_HEADER = (
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


def main():
    print('Patching: ' + INDEX_PATH)
    src = read_file(INDEX_PATH)
    nl = '\r\n' if '\r\n' in src else '\n'

    src, removed = strip_block(src, CSS_BEGIN, CSS_END)
    print('  [{}]   removed BCG CSS block'.format('ok' if removed else 'skip'))

    src, _ = replace_once(src, BCG_PERSONAL, PREVIOUS_PERSONAL,
                          'restored personal view (.eng-kpi version)', nl)

    src, _ = replace_once(src, BCG_FOCUS_HEADER, PREVIOUS_FOCUS_HEADER,
                          'restored focus tab header (gradient + 4-card)', nl)

    write_file(INDEX_PATH, src)
    print('Done.')


if __name__ == '__main__':
    main()
