# -*- coding: utf-8 -*-
"""
Rewrite the "Mes performances" (engagement scoreboard) page so it
reflects the new per-client engagement model.

Old: counted commitments against a global focus list (deprecated) and
manual palier targets (deprecated).

New: portfolio aggregation across the seller's claimed/file-assigned
clients with these metrics:
  * clients       — total clients in portfolio
  * gifts         — total gifts unlocked (May + May+June across clients)
  * atMin         — clients with ≥ ENG_CLIENT_MIN_PRODUCTS committed
  * totalGmv      — cumulative May+June GMV across the portfolio
  * won/ok/idle counts that mirror the paliers tab buckets

Personal view: branded hero + KPI grid + status breakdown bar.
Creator view : podium top 3 sorted by gifts → GMV, then table.
"""
import io, sys

P = '/sessions/vibrant-tender-mayer/mnt/Rehab app ( planner) - Copie/rigab_app/index.html'
src = io.open(P, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'

# --- 1) CSS for the new scoreboard widgets -------------------------------
CSS_BEGIN = '/* === SCOREBOARD REDESIGN — redesign_scoreboard.py === */'
CSS_END   = '/* === END SCOREBOARD REDESIGN === */'
if CSS_BEGIN in src and CSS_END in src:
    a = src.index(CSS_BEGIN); b = src.index(CSS_END) + len(CSS_END)
    e = b
    while e < len(src) and src[e] in ('\n', '\r'): e += 1
    st = a
    while st > 0 and src[st-1] in ('\n', '\r'): st -= 1
    src = src[:st] + src[e:]

CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  .sb-hero {\n'
    '    position: relative; overflow: hidden;\n'
    '    background: linear-gradient(135deg, var(--rf-orange, #f6624a) 0%, var(--rf-orange-dark, #d54b33) 100%);\n'
    '    color: #fff; border-radius: 16px;\n'
    '    padding: 20px 22px; margin: 0 0 14px;\n'
    '    box-shadow: 0 4px 14px rgba(246, 98, 74, .2);\n'
    '  }\n'
    '  .sb-hero::before {\n'
    '    content: ""; position: absolute;\n'
    '    inset-inline-end: -60px; top: -60px;\n'
    '    width: 200px; height: 200px; border-radius: 50%;\n'
    '    border: 10px dashed rgba(255,255,255,.18);\n'
    '    animation: rf-spin 60s linear infinite; pointer-events: none;\n'
    '  }\n'
    '  .sb-hero-eyebrow { font-size: 10px; font-weight: 800; letter-spacing: .15em; text-transform: uppercase; opacity: .85; }\n'
    '  .sb-hero-name    { font-size: 22px; font-weight: 800; line-height: 1.15; margin: 4px 0 0; letter-spacing: -.01em; }\n'
    '  .sb-hero-stats   {\n'
    '    display: flex; gap: 18px; flex-wrap: wrap; margin-top: 14px;\n'
    '    font-size: 12.5px; font-variant-numeric: tabular-nums; position: relative;\n'
    '  }\n'
    '  .sb-hero-stat b  { font-size: 20px; font-weight: 800; display: block; line-height: 1.1; }\n'
    '  .sb-hero-stat span { opacity: .85; font-size: 11px; letter-spacing: .04em; }\n'
    '\n'
    '  .sb-kpi-grid {\n'
    '    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));\n'
    '    gap: 10px; margin: 0 0 16px;\n'
    '  }\n'
    '  .sb-kpi {\n'
    '    background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;\n'
    '    padding: 14px 16px; display: flex; align-items: center; gap: 12px;\n'
    '    transition: border-color .12s, box-shadow .12s;\n'
    '  }\n'
    '  .sb-kpi:hover { border-color: #d1d5db; box-shadow: 0 2px 6px rgba(15, 23, 42, .06); }\n'
    '  .sb-kpi-icon {\n'
    '    width: 40px; height: 40px; border-radius: 10px;\n'
    '    display: inline-flex; align-items: center; justify-content: center;\n'
    '    font-size: 20px; flex-shrink: 0;\n'
    '  }\n'
    '  .sb-kpi-body  { flex: 1; min-width: 0; }\n'
    '  .sb-kpi-value {\n'
    '    font-size: 22px; font-weight: 800; color: #0f172a;\n'
    '    line-height: 1.1; letter-spacing: -.02em;\n'
    '    font-variant-numeric: tabular-nums;\n'
    '  }\n'
    '  .sb-kpi-label {\n'
    '    font-size: 10.5px; font-weight: 700; letter-spacing: .12em;\n'
    '    text-transform: uppercase; color: #6b7280; margin-top: 3px;\n'
    '  }\n'
    '  .sb-kpi--won  .sb-kpi-icon { background: #fff7ed; color: #c2410c; }\n'
    '  .sb-kpi--ok   .sb-kpi-icon { background: #f0fdf4; color: #15803d; }\n'
    '  .sb-kpi--idle .sb-kpi-icon { background: #f1f5f9; color: #475569; }\n'
    '  .sb-kpi--gmv  .sb-kpi-icon { background: #eef2ff; color: #4338ca; }\n'
    '\n'
    '  .sb-status {\n'
    '    background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;\n'
    '    padding: 16px 18px; margin: 0 0 14px;\n'
    '  }\n'
    '  .sb-status-title {\n'
    '    font-size: 10.5px; font-weight: 800; letter-spacing: .12em;\n'
    '    text-transform: uppercase; color: #6b7280; margin: 0 0 12px;\n'
    '  }\n'
    '  .sb-status-bar {\n'
    '    display: flex; height: 10px; border-radius: 99px; overflow: hidden;\n'
    '    background: #f1f5f9; margin: 0 0 12px;\n'
    '  }\n'
    '  .sb-status-bar > span { display: block; transition: width .6s cubic-bezier(.2,.7,.3,1); }\n'
    '  .sb-status-bar > span.won  { background: linear-gradient(90deg, #fdba74, var(--rf-orange-dark, #d54b33)); }\n'
    '  .sb-status-bar > span.ok   { background: linear-gradient(90deg, #4ade80, #16a34a); }\n'
    '  .sb-status-bar > span.idle { background: #cbd5e1; }\n'
    '  .sb-status-legend {\n'
    '    display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));\n'
    '    gap: 10px;\n'
    '  }\n'
    '  .sb-status-leg {\n'
    '    display: flex; align-items: center; gap: 8px;\n'
    '    font-size: 12px;\n'
    '  }\n'
    '  .sb-status-leg-dot {\n'
    '    width: 10px; height: 10px; border-radius: 99px; flex-shrink: 0;\n'
    '  }\n'
    '  .sb-status-leg .won  { background: var(--rf-orange-dark, #d54b33); }\n'
    '  .sb-status-leg .ok   { background: #16a34a; }\n'
    '  .sb-status-leg .idle { background: #cbd5e1; }\n'
    '  .sb-status-leg b   { color: #0f172a; font-weight: 800; font-variant-numeric: tabular-nums; }\n'
    '  .sb-status-leg span { color: #6b7280; font-size: 11px; }\n'
    '\n'
    '  /* Leaderboard (creator view) */\n'
    '  .sb-podium {\n'
    '    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));\n'
    '    gap: 12px; margin: 0 0 18px;\n'
    '  }\n'
    '  .sb-podium-card {\n'
    '    background: #fff; border: 2px solid; border-radius: 14px;\n'
    '    padding: 18px; text-align: center;\n'
    '  }\n'
    '  .sb-podium-card .medal { font-size: 28px; margin-bottom: 4px; }\n'
    '  .sb-podium-card .name  { font-size: 14px; font-weight: 800; color: #0f172a; }\n'
    '  .sb-podium-card .big   {\n'
    '    font-size: 28px; font-weight: 800; margin-top: 8px;\n'
    '    font-variant-numeric: tabular-nums; line-height: 1;\n'
    '  }\n'
    '  .sb-podium-card .meta  { font-size: 11px; color: #6b7280; margin-top: 6px; line-height: 1.4; }\n'
    '  .sb-podium-card.r1 { border-color: #fbbf24; }\n'
    '  .sb-podium-card.r1 .big { color: #d97706; }\n'
    '  .sb-podium-card.r2 { border-color: #94a3b8; }\n'
    '  .sb-podium-card.r2 .big { color: #475569; }\n'
    '  .sb-podium-card.r3 { border-color: #a3754f; }\n'
    '  .sb-podium-card.r3 .big { color: #92400e; }\n'
    '\n'
    '  .sb-table-wrap {\n'
    '    background: #fff; border: 1px solid #e5e7eb;\n'
    '    border-radius: 12px; overflow: hidden;\n'
    '  }\n'
    '  .sb-table {\n'
    '    width: 100%; border-collapse: collapse; font-size: 13px;\n'
    '    font-variant-numeric: tabular-nums;\n'
    '  }\n'
    '  .sb-table th {\n'
    '    text-align: start; padding: 10px 12px;\n'
    '    font-size: 10px; font-weight: 800; letter-spacing: .1em;\n'
    '    text-transform: uppercase; color: #6b7280;\n'
    '    background: #f9fafb;\n'
    '  }\n'
    '  .sb-table th.num { text-align: end; }\n'
    '  .sb-table td { padding: 10px 12px; border-top: 1px solid #f1f5f9; }\n'
    '  .sb-table td.num { text-align: end; font-weight: 700; color: #0f172a; }\n'
    '\n'
    '  @media (max-width: 600px) {\n'
    '    .sb-hero { padding: 16px 18px; border-radius: 14px; }\n'
    '    .sb-hero-name { font-size: 18px; }\n'
    '    .sb-hero-stat b { font-size: 17px; }\n'
    '    .sb-kpi-grid { grid-template-columns: 1fr 1fr; }\n'
    '    .sb-kpi-value { font-size: 19px; }\n'
    '  }\n'
    + CSS_END
)

css_anchor = '/* === END PALIER SECTIONS === */'
if css_anchor not in src:
    print('  [FAIL] CSS anchor not found'); sys.exit(2)
src = src.replace(css_anchor, css_anchor + nl + '  ' + CSS_BLOCK.replace('\n', nl), 1)
print('  [ok]   injected scoreboard CSS')


# --- 2) Wholesale replace gmvRenderEngagementScoreboard ----------------
# Find the function start and the closing brace (the one before the
# "// ====" client-assignment-pool comment).
START_MARK = 'function gmvRenderEngagementScoreboard(panel, mySeller, isCreator) {'
END_MARK_BEFORE = ('// =========================================================================' + nl + '// Client assignment pool — sellers claim wholesale clients from a shared')

if START_MARK not in src or END_MARK_BEFORE not in src:
    print('  [FAIL] scoreboard function boundaries not found'); sys.exit(2)

s_idx = src.index(START_MARK)
e_idx_anchor = src.index(END_MARK_BEFORE)
# Walk back to the closing brace of the function.
e_idx = src.rfind('}', s_idx, e_idx_anchor)
if e_idx == -1:
    print('  [FAIL] scoreboard closing brace not found'); sys.exit(2)
# Include trailing newline.
end = e_idx + 1
while end < len(src) and src[end] in ('\n', '\r'): end += 1


NEW_FN = (
    'function gmvRenderEngagementScoreboard(panel, mySeller, isCreator) {\n'
    '  if (!panel) return;\n'
    '  panel.setAttribute(\'dir\', engLang() === \'ar\' ? \'rtl\' : \'ltr\');\n'
    '  const period = gmvCurrentPeriodKey();\n'
    '  const fmt = n => Math.round(n || 0).toLocaleString(\'en-US\');\n'
    '\n'
    '  // ---- Helpers: enumerate a seller\'s clients (claims OR file). ----\n'
    '  const phonesForSeller = (seller) => {\n'
    '    const seen = new Set();\n'
    '    const out = [];\n'
    '    Object.entries(gmv.clients || {}).forEach(([phone, c]) => {\n'
    '      const claim = gmvClientAssignments && gmvClientAssignments.byPhone ? gmvClientAssignments.byPhone[phone] : null;\n'
    '      const assigned = (claim && claim.seller) || (c && c.seller) || \'\';\n'
    '      if (assigned === seller && !seen.has(phone)) { seen.add(phone); out.push(phone); }\n'
    '    });\n'
    '    Object.entries((gmvClientAssignments && gmvClientAssignments.byPhone) || {}).forEach(([phone, a]) => {\n'
    '      if (a.seller === seller && !seen.has(phone)) { seen.add(phone); out.push(phone); }\n'
    '    });\n'
    '    return out;\n'
    '  };\n'
    '\n'
    '  // ---- Aggregate stats for one seller across their portfolio. ----\n'
    '  const computeFor = (seller) => {\n'
    '    const phones = phonesForSeller(seller);\n'
    '    const commit = gmvEngagement.commitments[seller] || {};\n'
    '    const cFocus = commit.clientFocus || {};\n'
    '    const caM1 = gmvCaPerClientPeriod(ENG_PERIOD_M1);\n'
    '    const caM2 = gmvCaPerClientPeriod(ENG_PERIOD_M2);\n'
    '    const sortedPaliers = (gmvEngagement.paliers || []).slice().sort((a, b) => (a.palier || 0) - (b.palier || 0));\n'
    '    let totalGmv = 0;\n'
    '    let palierMax = 0;\n'
    '    let m1Gifts = 0, bothGifts = 0;\n'
    '    let won = 0, atMin = 0, idle = 0;\n'
    '    phones.forEach(phone => {\n'
    '      const c1 = caM1[phone] || 0;\n'
    '      const c2 = caM2[phone] || 0;\n'
    '      const cBoth = c1 + c2;\n'
    '      totalGmv += cBoth;\n'
    '      const ach = gmvAchievedPalier(cBoth);\n'
    '      if (ach && ach.palier > palierMax) palierMax = ach.palier;\n'
    '      const targetP = sortedPaliers.find(p => (p.threshold || 0) > cBoth) || null;\n'
    '      const myProds = Object.keys(cFocus[phone] || {}).filter(c => cFocus[phone][c] && cFocus[phone][c].selected);\n'
    '      const prodOk = myProds.length >= ENG_CLIENT_MIN_PRODUCTS;\n'
    '      const m1Count   = gmvClientAchievedM1(seller, phone, myProds);\n'
    '      const bothCount = gmvClientAchievedBoth(seller, phone, myProds);\n'
    '      const m1Open   = !!(targetP && c1    >= (targetP.threshold || 0) && m1Count   >= ENG_CLIENT_MILESTONE_M1);\n'
    '      const bothOpen = !!(targetP && cBoth >= (targetP.threshold || 0) && bothCount >= ENG_CLIENT_MILESTONE_BOTH);\n'
    '      if (m1Open) m1Gifts++;\n'
    '      if (bothOpen) bothGifts++;\n'
    '      if (m1Open || bothOpen) won++;\n'
    '      else if (prodOk) atMin++;\n'
    '      else idle++;\n'
    '    });\n'
    '    const giftsTotal = m1Gifts + bothGifts;\n'
    '    return {\n'
    '      seller,\n'
    '      clients: phones.length,\n'
    '      totalGmv,\n'
    '      palierMax,\n'
    '      m1Gifts, bothGifts, giftsTotal,\n'
    '      won, atMin, idle,\n'
    '    };\n'
    '  };\n'
    '\n'
    '  // ===== PERSONAL VIEW =====\n'
    '  if (mySeller && !isCreator) {\n'
    '    const me = computeFor(mySeller);\n'
    '    if (me.clients === 0) {\n'
    '      panel.innerHTML = `<div style=\"padding:40px 24px; text-align:center; background:#f8fafc; border:1px dashed #cbd5e1; border-radius:14px;\">\n'
    '        <div style=\"font-size:36px; margin-bottom:10px;\">📈</div>\n'
    '        <div style=\"font-size:14px; color:#475569; font-weight:600;\">${engT(\'sc_no_data\')}</div>\n'
    '      </div>`;\n'
    '      return;\n'
    '    }\n'
    '    const tot = me.won + me.atMin + me.idle;\n'
    '    const pctWon  = tot ? (me.won  / tot) * 100 : 0;\n'
    '    const pctOk   = tot ? (me.atMin / tot) * 100 : 0;\n'
    '    const pctIdle = tot ? (me.idle / tot) * 100 : 0;\n'
    '    panel.innerHTML = `\n'
    '      <section class=\"sb-hero\">\n'
    '        <div class=\"sb-hero-eyebrow\">${engT(\'sc_my_perf\')} · ${period}</div>\n'
    '        <h2 class=\"sb-hero-name\">${gmvEscapeHtmlEng(me.seller)}</h2>\n'
    '        <div class=\"sb-hero-stats\">\n'
    '          <div class=\"sb-hero-stat\"><b>${me.clients}</b><span>${engT(\'sb_stat_clients\')}</span></div>\n'
    '          <div class=\"sb-hero-stat\"><b>${me.giftsTotal}</b><span>${engT(\'sb_stat_gifts\')}</span></div>\n'
    '          <div class=\"sb-hero-stat\"><b>${fmt(me.totalGmv)}</b><span>MAD · ${engT(\'sb_stat_gmv\')}</span></div>\n'
    '        </div>\n'
    '      </section>\n'
    '\n'
    '      <div class=\"sb-kpi-grid\">\n'
    '        <article class=\"sb-kpi sb-kpi--idle\">\n'
    '          <div class=\"sb-kpi-icon\">👥</div>\n'
    '          <div class=\"sb-kpi-body\">\n'
    '            <div class=\"sb-kpi-value\">${me.clients}</div>\n'
    '            <div class=\"sb-kpi-label\">${engT(\'sb_kpi_clients\')}</div>\n'
    '          </div>\n'
    '        </article>\n'
    '        <article class=\"sb-kpi sb-kpi--won\">\n'
    '          <div class=\"sb-kpi-icon\">🎁</div>\n'
    '          <div class=\"sb-kpi-body\">\n'
    '            <div class=\"sb-kpi-value\">${me.giftsTotal}</div>\n'
    '            <div class=\"sb-kpi-label\">${engT(\'sb_kpi_gifts\')}</div>\n'
    '          </div>\n'
    '        </article>\n'
    '        <article class=\"sb-kpi sb-kpi--ok\">\n'
    '          <div class=\"sb-kpi-icon\">✓</div>\n'
    '          <div class=\"sb-kpi-body\">\n'
    '            <div class=\"sb-kpi-value\">${me.atMin}</div>\n'
    '            <div class=\"sb-kpi-label\">${engT(\'sb_kpi_at_min\')}</div>\n'
    '          </div>\n'
    '        </article>\n'
    '        <article class=\"sb-kpi sb-kpi--gmv\">\n'
    '          <div class=\"sb-kpi-icon\">💰</div>\n'
    '          <div class=\"sb-kpi-body\">\n'
    '            <div class=\"sb-kpi-value\">${fmt(me.totalGmv)}</div>\n'
    '            <div class=\"sb-kpi-label\">MAD · ${engT(\'sb_kpi_total_gmv\')}</div>\n'
    '          </div>\n'
    '        </article>\n'
    '      </div>\n'
    '\n'
    '      <section class=\"sb-status\">\n'
    '        <div class=\"sb-status-title\">${engT(\'sb_status_title\')}</div>\n'
    '        <div class=\"sb-status-bar\">\n'
    '          ${me.won  > 0 ? `<span class=\"won\"  style=\"width:${pctWon}%\"></span>` : \'\'}\n'
    '          ${me.atMin > 0 ? `<span class=\"ok\"   style=\"width:${pctOk}%\"></span>` : \'\'}\n'
    '          ${me.idle > 0 ? `<span class=\"idle\" style=\"width:${pctIdle}%\"></span>` : \'\'}\n'
    '        </div>\n'
    '        <div class=\"sb-status-legend\">\n'
    '          <div class=\"sb-status-leg\"><span class=\"sb-status-leg-dot won\"></span><div><b>${me.won}</b> <span>${engT(\'pal_sec_won_t\')}</span></div></div>\n'
    '          <div class=\"sb-status-leg\"><span class=\"sb-status-leg-dot ok\"></span><div><b>${me.atMin}</b> <span>${engT(\'pal_sec_ok_t\')}</span></div></div>\n'
    '          <div class=\"sb-status-leg\"><span class=\"sb-status-leg-dot idle\"></span><div><b>${me.idle}</b> <span>${engT(\'pal_sec_idle_t\')}</span></div></div>\n'
    '        </div>\n'
    '      </section>`;\n'
    '    return;\n'
    '  }\n'
    '\n'
    '  // ===== CREATOR / VIEWER VIEW — LEADERBOARD =====\n'
    '  const allSellers = new Set(Object.values(gmv.clients || {}).map(c => c && c.seller).filter(Boolean));\n'
    '  Object.values((gmvClientAssignments && gmvClientAssignments.byPhone) || {}).forEach(a => { if (a.seller) allSellers.add(a.seller); });\n'
    '  const stats = Array.from(allSellers).map(computeFor)\n'
    '    .sort((a, b) => (b.giftsTotal - a.giftsTotal) || (b.totalGmv - a.totalGmv) || (b.atMin - a.atMin));\n'
    '  if (!stats.length) {\n'
    '    panel.innerHTML = `<div style=\"padding:40px 24px; text-align:center; background:#f8fafc; border:1px dashed #cbd5e1; border-radius:14px; color:#64748b; font-size:13px;\">${engT(\'sc_no_data\')}</div>`;\n'
    '    return;\n'
    '  }\n'
    '  const totalGifts = stats.reduce((s, x) => s + x.giftsTotal, 0);\n'
    '  const totalClients = stats.reduce((s, x) => s + x.clients, 0);\n'
    '  const totalGmv = stats.reduce((s, x) => s + x.totalGmv, 0);\n'
    '  const podium = stats.slice(0, 3);\n'
    '  const rest = stats.slice(3);\n'
    '  const podiumCard = (s, i) => {\n'
    '    const medals = [\'🥇\', \'🥈\', \'🥉\'];\n'
    '    const cls = [\'r1\', \'r2\', \'r3\'][i];\n'
    '    return `<article class=\"sb-podium-card ${cls}\">\n'
    '      <div class=\"medal\">${medals[i]}</div>\n'
    '      <div class=\"name\">${gmvEscapeHtmlEng(s.seller)}</div>\n'
    '      <div class=\"big\">${s.giftsTotal}</div>\n'
    '      <div class=\"meta\">${engT(\'sb_kpi_gifts\')}<br/><span>${s.clients} ${engT(\'sb_stat_clients\').toLowerCase()} · ${fmt(s.totalGmv)} MAD</span></div>\n'
    '    </article>`;\n'
    '  };\n'
    '  panel.innerHTML = `\n'
    '    <section class=\"sb-hero\">\n'
    '      <div class=\"sb-hero-eyebrow\">${engT(\'sc_leaderboard\')} · ${period}</div>\n'
    '      <h2 class=\"sb-hero-name\">${stats.length} ${engT(\'sc_seller\').toLowerCase()}(s)</h2>\n'
    '      <div class=\"sb-hero-stats\">\n'
    '        <div class=\"sb-hero-stat\"><b>${totalClients}</b><span>${engT(\'sb_stat_clients\')}</span></div>\n'
    '        <div class=\"sb-hero-stat\"><b>${totalGifts}</b><span>${engT(\'sb_stat_gifts\')}</span></div>\n'
    '        <div class=\"sb-hero-stat\"><b>${fmt(totalGmv)}</b><span>MAD · ${engT(\'sb_stat_gmv\')}</span></div>\n'
    '      </div>\n'
    '    </section>\n'
    '    ${podium.length ? `<div class=\"sb-podium\">${podium.map(podiumCard).join(\'\')}</div>` : \'\'}\n'
    '    ${rest.length ? `\n'
    '      <div class=\"sb-table-wrap\">\n'
    '        <table class=\"sb-table\">\n'
    '          <thead><tr>\n'
    '            <th>${engT(\'sc_rank\')}</th>\n'
    '            <th>${engT(\'sc_seller\')}</th>\n'
    '            <th class=\"num\">${engT(\'sb_kpi_clients\')}</th>\n'
    '            <th class=\"num\">${engT(\'sb_kpi_gifts\')}</th>\n'
    '            <th class=\"num\">${engT(\'sb_kpi_at_min\')}</th>\n'
    '            <th class=\"num\">${engT(\'sb_kpi_total_gmv\')} MAD</th>\n'
    '          </tr></thead>\n'
    '          <tbody>\n'
    '            ${rest.map((s, i) => `<tr>\n'
    '              <td style=\"color:#94a3b8;\">${i + 4}</td>\n'
    '              <td style=\"font-weight:600;\">${gmvEscapeHtmlEng(s.seller)}</td>\n'
    '              <td class=\"num\">${s.clients}</td>\n'
    '              <td class=\"num\" style=\"color:${s.giftsTotal > 0 ? \'#c2410c\' : \'#94a3b8\'};\">${s.giftsTotal}</td>\n'
    '              <td class=\"num\">${s.atMin}</td>\n'
    '              <td class=\"num\">${fmt(s.totalGmv)}</td>\n'
    '            </tr>`).join(\'\')}\n'
    '          </tbody>\n'
    '        </table>\n'
    '      </div>` : \'\'}`;\n'
    '}\n'
)

src = src[:s_idx] + NEW_FN.replace('\n', nl) + src[end:]
print('  [ok]   replaced gmvRenderEngagementScoreboard')


# --- 3) Add new i18n keys ----------------------------------------------
def add_i18n(s, anchor, addition, label):
    o = anchor.replace('\n', nl)
    n = anchor.replace('\n', nl) + addition.replace('\n', nl)
    if n in s and o not in s: print('  [skip] ' + label); return s
    if o not in s: print('  [FAIL] ' + label); sys.exit(2)
    if s.count(o) != 1: print('  [FAIL] ' + label + ' (count ' + str(s.count(o)) + ')'); sys.exit(2)
    print('  [ok]   ' + label)
    return s.replace(o, n, 1)

src = add_i18n(src,
    "    pal_sec_idle_t: 'Pas encore actifs', pal_sec_idle_d: 'Moins de 10 produits engagés.',\n",
    "    sb_stat_clients: 'Clients', sb_stat_gifts: 'Cadeaux ouverts', sb_stat_gmv: 'GMV cumulé',\n"
    "    sb_kpi_clients: 'Clients', sb_kpi_gifts: 'Cadeaux ouverts', sb_kpi_at_min: 'Minimum atteint', sb_kpi_total_gmv: 'GMV total',\n"
    "    sb_status_title: 'Statut de mon portefeuille',\n",
    'FR scoreboard i18n')

src = add_i18n(src,
    "    pal_sec_idle_t: 'Not active yet',    pal_sec_idle_d: 'Fewer than 10 products committed.',\n",
    "    sb_stat_clients: 'Clients', sb_stat_gifts: 'Gifts open', sb_stat_gmv: 'Cumulative GMV',\n"
    "    sb_kpi_clients: 'Clients', sb_kpi_gifts: 'Gifts open', sb_kpi_at_min: 'At minimum', sb_kpi_total_gmv: 'Total GMV',\n"
    "    sb_status_title: 'My portfolio status',\n",
    'EN scoreboard i18n')

src = add_i18n(src,
    "    pal_sec_idle_t: 'لم ينشط بعد',    pal_sec_idle_d: 'أقل من 10 منتجات ملتزم بها.',\n",
    "    sb_stat_clients: 'الزبناء', sb_stat_gifts: 'الهدايا المفتوحة', sb_stat_gmv: 'GMV التراكمي',\n"
    "    sb_kpi_clients: 'الزبناء', sb_kpi_gifts: 'الهدايا المفتوحة', sb_kpi_at_min: 'الحد الأدنى مبلوغ', sb_kpi_total_gmv: 'GMV الإجمالي',\n"
    "    sb_status_title: 'حالة محفظتي',\n",
    'AR scoreboard i18n')


io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
