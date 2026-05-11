# -*- coding: utf-8 -*-
"""
Per-client engagement model.

User spec: "for each client the seller should choose minimum products,
where he should reach the minimum (as we did before but now for clients)
for 5 products for 05.2026 to open a threshold gift for the month mai,
and 10 for the month of both 05.2025 and 06.2025. (the threshold can be
reached by other products from the list or other products not on the list)"

Implementation:
  * Add ENG_CLIENT_MIN_PRODUCTS = 10, ENG_CLIENT_MILESTONE_M1 = 5,
    ENG_CLIENT_MILESTONE_BOTH = 10.
  * Per-client product commitments stored on the in-memory commitment
    as `clientFocus[phone][code] = {selected:true}`. Persisted by stuffing
    into the existing `focus` JSONB column under the `__byClient` key
    (no Supabase schema change needed).
  * gmvLoadEngagement extracts __byClient into commitment.clientFocus.
  * gmvSaveEngagementCommitment accepts `patch.clientFocus`, merges it
    back into the focus blob for storage.
  * Add helpers:
      gmvComputeSoldForSellerClient(seller, phone, period)
      gmvClientAchievedM1(seller, phone, codes)
      gmvClientAchievedBoth(seller, phone, codes)
      gmvCaPerClientPeriod(period)            -> phone -> GMV (any products)
  * Replace gmvRenderEngagementPaliers with a card-based UI:
      - Per-client palier target dropdown (existing).
      - Expandable focus-products picker per client (new).
      - May gift status row (5 products at min + GMV ≥ palier threshold).
      - May+June gift status row (10 cumulative + GMV ≥ palier threshold).

Run via bash (from session):
  python3 /sessions/vibrant-tender-mayer/mnt/Bons/add_per_client_engagement.py
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


# ---- Patch 1: gmvLoadEngagement extracts __byClient out of focus ------
OLD_LOAD = (
    "    if (ce && Array.isArray(ce.data)) {\n"
    "      const map = {};\n"
    "      ce.data.forEach(r => { map[r.seller] = r; });\n"
    "      gmvEngagement.commitments = map;\n"
    "    }\n"
)
NEW_LOAD = (
    "    if (ce && Array.isArray(ce.data)) {\n"
    "      const map = {};\n"
    "      ce.data.forEach(r => {\n"
    "        // Per-client product commitments are stashed under focus.__byClient\n"
    "        // so we don't need a Supabase schema change. Extract into\n"
    "        // commitment.clientFocus for the in-memory shape.\n"
    "        const f = (r && r.focus && typeof r.focus === 'object') ? r.focus : {};\n"
    "        const byClient = (f && f.__byClient && typeof f.__byClient === 'object') ? f.__byClient : {};\n"
    "        const clean = {};\n"
    "        Object.keys(f || {}).forEach(k => { if (k !== '__byClient') clean[k] = f[k]; });\n"
    "        r.focus = clean;\n"
    "        r.clientFocus = byClient;\n"
    "        map[r.seller] = r;\n"
    "      });\n"
    "      gmvEngagement.commitments = map;\n"
    "    }\n"
)


# ---- Patch 2: gmvSaveEngagementCommitment accepts clientFocus + merges
OLD_SAVE = (
    "async function gmvSaveEngagementCommitment(seller, period, patch) {\n"
    "  if (typeof sb === 'undefined' || !sb || !sbUser) throw new Error('Not signed in.');\n"
    "  const existing = gmvEngagement.commitments[seller] || {};\n"
    "  const row = {\n"
    "    seller, period,\n"
    "    focus: patch.focus || existing.focus || {},\n"
    "    paliers: patch.paliers || existing.paliers || {},\n"
    "    updated_at: new Date().toISOString(),\n"
    "  };\n"
    "  const { error } = await sb.from('seller_engagements').upsert(row, { onConflict: 'seller,period' });\n"
    "  if (error) throw new Error(error.message || String(error));\n"
    "  gmvEngagement.commitments[seller] = row;\n"
    "}\n"
)
NEW_SAVE = (
    "async function gmvSaveEngagementCommitment(seller, period, patch) {\n"
    "  if (typeof sb === 'undefined' || !sb || !sbUser) throw new Error('Not signed in.');\n"
    "  const existing = gmvEngagement.commitments[seller] || {};\n"
    "  const newFocus       = (patch.focus       !== undefined) ? patch.focus       : (existing.focus       || {});\n"
    "  const newClientFocus = (patch.clientFocus !== undefined) ? patch.clientFocus : (existing.clientFocus || {});\n"
    "  const newPaliers     = (patch.paliers     !== undefined) ? patch.paliers     : (existing.paliers     || {});\n"
    "  // Stash per-client commitments inside the focus JSONB under __byClient\n"
    "  // so the existing Supabase schema works without a migration.\n"
    "  const focusBlob = Object.assign({}, newFocus);\n"
    "  if (newClientFocus && Object.keys(newClientFocus).length) {\n"
    "    focusBlob.__byClient = newClientFocus;\n"
    "  }\n"
    "  const row = {\n"
    "    seller, period,\n"
    "    focus: focusBlob,\n"
    "    paliers: newPaliers,\n"
    "    updated_at: new Date().toISOString(),\n"
    "  };\n"
    "  const { error } = await sb.from('seller_engagements').upsert(row, { onConflict: 'seller,period' });\n"
    "  if (error) throw new Error(error.message || String(error));\n"
    "  // Store split shape in memory so the rest of the code reads focus\n"
    "  // (global) without seeing __byClient leak through.\n"
    "  gmvEngagement.commitments[seller] = {\n"
    "    seller, period,\n"
    "    focus: newFocus,\n"
    "    clientFocus: newClientFocus,\n"
    "    paliers: newPaliers,\n"
    "    updated_at: row.updated_at,\n"
    "  };\n"
    "}\n"
)


# ---- Patch 3: helpers right after gmvAchievedPalier --------------------
HELPERS_ANCHOR = (
    "function gmvAchievedPalier(ca) {\n"
    "  let best = null;\n"
    "  (gmvEngagement.paliers || []).forEach(p => {\n"
    "    if ((ca || 0) >= (p.threshold || 0) && (!best || p.palier > best.palier)) best = p;\n"
    "  });\n"
    "  return best;\n"
    "}\n"
)
HELPERS_NEW = HELPERS_ANCHOR + (
    "\n"
    "// ===== Per-client engagement helpers =====================================\n"
    "// Sellers commit a list of focus products PER CLIENT. Achievement is\n"
    "// per-product per-client: a SKU is 'achieved' for client X when\n"
    "// delivered qty to X >= the SKU's min in the relevant period.\n"
    "//   Milestone M1   = ENG_CLIENT_MILESTONE_M1 SKUs achieved by end of May\n"
    "//   Milestone Both = ENG_CLIENT_MILESTONE_BOTH SKUs achieved with\n"
    "//                    cumulative qty across May+June.\n"
    "// The palier GMV threshold is met by the client's GMV across ANY\n"
    "// products (focus or not) — this is independent of the milestone\n"
    "// product list.\n"
    "const ENG_CLIENT_MIN_PRODUCTS  = 10;\n"
    "const ENG_CLIENT_MILESTONE_M1   = 5;\n"
    "const ENG_CLIENT_MILESTONE_BOTH = 10;\n"
    "\n"
    "// Per-(seller, phone, period) qty/gmv for each focus product.\n"
    "function gmvComputeSoldForSellerClient(seller, phone, period) {\n"
    "  const out = {};\n"
    "  const useFulfillOrders = (typeof fulfill !== 'undefined' && fulfill && Array.isArray(fulfill.orders) && fulfill.orders.length);\n"
    "  const sourceLines = useFulfillOrders ? fulfill.orders : (gmv.orders || []);\n"
    "  sourceLines.forEach(o => {\n"
    "    if (!o || !o.productCode || o.phone !== phone) return;\n"
    "    if (!gmvEngagement.focusProducts[o.productCode]) return;\n"
    "    const d = o.date instanceof Date ? o.date : (o.date ? new Date(o.date) : null);\n"
    "    if (!d || isNaN(d.getTime())) return;\n"
    "    const key = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');\n"
    "    if (key !== period) return;\n"
    "    const cl = (gmv.clients || {})[o.phone] || {};\n"
    "    const assigned = (gmvClientAssignments && gmvClientAssignments.byPhone && gmvClientAssignments.byPhone[o.phone] && gmvClientAssignments.byPhone[o.phone].seller) || cl.seller || '';\n"
    "    if (assigned !== seller) return;\n"
    "    if (!out[o.productCode]) out[o.productCode] = { qty: 0, gmv: 0 };\n"
    "    out[o.productCode].qty += (typeof o.qty === 'number' ? o.qty : 1);\n"
    "    out[o.productCode].gmv += (o.amount || 0);\n"
    "  });\n"
    "  return out;\n"
    "}\n"
    "\n"
    "function gmvClientAchievedM1(seller, phone, codes) {\n"
    "  const sold = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M1);\n"
    "  let achieved = 0;\n"
    "  (codes || []).forEach(code => {\n"
    "    const meta = gmvEngagement.focusProducts[code] || {};\n"
    "    const s = sold[code] || { qty: 0 };\n"
    "    if (meta.min && s.qty >= meta.min) achieved++;\n"
    "  });\n"
    "  return achieved;\n"
    "}\n"
    "\n"
    "function gmvClientAchievedBoth(seller, phone, codes) {\n"
    "  const m1 = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M1);\n"
    "  const m2 = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M2);\n"
    "  let achieved = 0;\n"
    "  (codes || []).forEach(code => {\n"
    "    const meta = gmvEngagement.focusProducts[code] || {};\n"
    "    const q = ((m1[code] && m1[code].qty) || 0) + ((m2[code] && m2[code].qty) || 0);\n"
    "    if (meta.min && q >= meta.min) achieved++;\n"
    "  });\n"
    "  return achieved;\n"
    "}\n"
    "\n"
    "// Total client GMV (any products, focus or not) for a specific period.\n"
    "function gmvCaPerClientPeriod(period) {\n"
    "  const out = {};\n"
    "  (gmv.orders || []).forEach(o => {\n"
    "    if (!o) return;\n"
    "    const d = o.date instanceof Date ? o.date : (o.date ? new Date(o.date) : null);\n"
    "    if (!d || isNaN(d.getTime())) return;\n"
    "    const key = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');\n"
    "    if (key !== period) return;\n"
    "    out[o.phone] = (out[o.phone] || 0) + (o.amount || 0);\n"
    "  });\n"
    "  return out;\n"
    "}\n"
)


# ---- Patch 4: replace gmvRenderEngagementPaliers wholesale ------------
OLD_PALIERS = (
    "function gmvRenderEngagementPaliers(panel, mySeller, isCreator) {\n"
    "  if (!panel) return;\n"
    "  if (!gmvEngagement.paliers.length) {\n"
    "    panel.innerHTML = '<div style=\"padding:24px; color:#94a3b8; text-align:center; font-size:13px;\">No paliers defined yet. ' + (isCreator ? 'Upload a paliers file above.' : 'Ask the creator to upload the paliers file.') + '</div>';\n"
    "    return;\n"
    "  }\n"
    "  if (!mySeller && !isCreator) {\n"
    "    panel.innerHTML = '<div style=\"padding:24px; color:#94a3b8; text-align:center; font-size:13px;\">Sign in as a seller to commit and track paliers.</div>';\n"
    "    return;\n"
    "  }\n"
    "  const period = gmvCurrentPeriodKey();\n"
    "  const seller = mySeller || '(creator)';\n"
    "  const commitment = (gmvEngagement.commitments[seller] || {}).paliers || {};\n"
    "  // Find this seller's claimed clients.\n"
    "  const myPhones = new Set();\n"
    "  Object.entries(gmvClientAssignments.byPhone || {}).forEach(([phone, a]) => {\n"
    "    if (a.seller === seller) myPhones.add(phone);\n"
    "  });\n"
    "  if (!myPhones.size) {\n"
    "    panel.innerHTML = '<div style=\"padding:24px; color:#94a3b8; text-align:center; font-size:13px;\">No claimed clients yet. Go to \"My clients\" tab to claim some.</div>';\n"
    "    return;\n"
    "  }\n"
    "  const ca = gmvComputeCaPerClient();\n"
    "  const palierOpts = ['<option value=\"0\">— No target —</option>'].concat(\n"
    "    gmvEngagement.paliers.map(p => `<option value=\"${p.palier}\">Palier ${p.palier} (${(p.threshold || 0).toLocaleString()} MAD)</option>`)\n"
    "  ).join('');\n"
    "  let html = `<table style=\"width:100%; border-collapse:collapse; font-size:13px; background:#fff; border:1px solid #e2e8f0; border-radius:8px; overflow:hidden;\">\n"
    "    <thead><tr style=\"background:#f8fafc;\">\n"
    "      <th style=\"text-align:left; padding:8px 10px; font-size:11px; color:#64748b;\">Client</th>\n"
    "      <th style=\"text-align:left; padding:8px 10px; font-size:11px; color:#64748b;\">Phone</th>\n"
    "      <th style=\"text-align:left; padding:8px 10px; font-size:11px; color:#64748b;\">Palier ciblé</th>\n"
    "      <th style=\"text-align:right; padding:8px 10px; font-size:11px; color:#64748b;\">CA actuel</th>\n"
    "      <th style=\"text-align:left; padding:8px 10px; font-size:11px; color:#64748b;\">Palier atteint</th>\n"
    "      <th style=\"text-align:left; padding:8px 10px; font-size:11px; color:#64748b;\">Récompense (atteint)</th>\n"
    "    </tr></thead><tbody>`;\n"
    "  Array.from(myPhones).forEach(phone => {\n"
    "    const cl = (gmv.clients || {})[phone] || {};\n"
    "    const target = commitment[phone] || 0;\n"
    "    const cur = ca[phone] || 0;\n"
    "    const ach = gmvAchievedPalier(cur);\n"
    "    const targetP = (gmvEngagement.paliers || []).find(p => p.palier === parseInt(target));\n"
    "    const hitTarget = ach && targetP && ach.palier >= targetP.palier;\n"
    "    const rowBg = hitTarget ? 'background:#f0fdf4;' : '';\n"
    "    html += `<tr style=\"${rowBg} border-top:1px solid #f1f5f9;\">\n"
    "      <td style=\"padding:6px 10px; font-weight:600;\">${gmvEscapeHtmlEng(cl.name || '(no name)')}</td>\n"
    "      <td style=\"padding:6px 10px; font-family:monospace; font-size:12px; color:#475569;\">${gmvEscapeHtmlEng(phone)}</td>\n"
    "      <td style=\"padding:6px 10px;\">\n"
    "        <select data-eng-palier=\"${gmvEscapeHtmlEng(phone)}\" style=\"padding:3px 6px; border:1px solid #cbd5e1; border-radius:4px; font-size:12px;\">\n"
    "          ${palierOpts.replace('value=\"' + target + '\"', 'value=\"' + target + '\" selected')}\n"
    "        </select>\n"
    "      </td>\n"
    "      <td style=\"padding:6px 10px; text-align:right; font-weight:600;\">${Math.round(cur).toLocaleString()} MAD</td>\n"
    "      <td style=\"padding:6px 10px;\">${ach ? `<span style=\"background:#dbeafe; color:#1e40af; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600;\">Palier ${ach.palier}</span>` : '<span style=\"color:#94a3b8; font-size:11px;\">aucun</span>'}</td>\n"
    "      <td style=\"padding:6px 10px; font-size:11px; color:#64748b;\">${ach ? gmvEscapeHtmlEng(ach.prize1 || '') : '—'}</td>\n"
    "    </tr>`;\n"
    "  });\n"
    "  html += `</tbody></table>`;\n"
    "  panel.innerHTML = `\n"
    "    <div style=\"display:flex; gap:8px; margin:0 0 10px;\">\n"
    "      <span style=\"font-size:13px;\"><b>${myPhones.size}</b> claimed client(s)</span>\n"
    "      <button type=\"button\" id=\"engSavePaliers\" class=\"btn btn-primary\" style=\"margin-left:auto; font-size:12px;\">Save my engagement</button>\n"
    "    </div>${html}`;\n"
    "  const saveBtn = document.getElementById('engSavePaliers');\n"
    "  if (saveBtn) saveBtn.addEventListener('click', async () => {\n"
    "    const paliers = {};\n"
    "    panel.querySelectorAll('[data-eng-palier]').forEach(s => {\n"
    "      const v = parseInt(s.value); if (v > 0) paliers[s.dataset.engPalier] = v;\n"
    "    });\n"
    "    try { await gmvSaveEngagementCommitment(seller, period, { paliers }); alert('Saved.'); }\n"
    "    catch (e) { alert('Save failed: ' + (e.message || e)); }\n"
    "  });\n"
    "}\n"
)

NEW_PALIERS = (
    "function gmvRenderEngagementPaliers(panel, mySeller, isCreator) {\n"
    "  if (!panel) return;\n"
    "  panel.setAttribute('dir', engLang() === 'ar' ? 'rtl' : 'ltr');\n"
    "  if (!gmvEngagement.paliers.length) {\n"
    "    panel.innerHTML = '<div style=\"padding:24px; color:#94a3b8; text-align:center; font-size:13px;\">' + engT('pal_no_paliers') + '</div>';\n"
    "    return;\n"
    "  }\n"
    "  if (!mySeller && !isCreator) {\n"
    "    panel.innerHTML = '<div style=\"padding:24px; color:#94a3b8; text-align:center; font-size:13px;\">' + engT('eng_signin_seller') + '</div>';\n"
    "    return;\n"
    "  }\n"
    "  const period   = gmvCurrentPeriodKey();\n"
    "  const seller   = mySeller || '(creator)';\n"
    "  const commit   = gmvEngagement.commitments[seller] || {};\n"
    "  const palTgts  = commit.paliers     || {};\n"
    "  const cFocus   = commit.clientFocus || {};\n"
    "  // Sorted, claimed client phones for this seller.\n"
    "  const myPhones = [];\n"
    "  Object.entries(gmvClientAssignments.byPhone || {}).forEach(([phone, a]) => {\n"
    "    if (a.seller === seller) myPhones.push(phone);\n"
    "  });\n"
    "  if (!myPhones.length) {\n"
    "    panel.innerHTML = '<div style=\"padding:24px; color:#94a3b8; text-align:center; font-size:13px;\">' + engT('pal_no_clients') + '</div>';\n"
    "    return;\n"
    "  }\n"
    "  myPhones.sort((a, b) => {\n"
    "    const na = (((gmv.clients || {})[a] || {}).name || '').toLowerCase();\n"
    "    const nb = (((gmv.clients || {})[b] || {}).name || '').toLowerCase();\n"
    "    return na.localeCompare(nb);\n"
    "  });\n"
    "  const focusCodes = Object.keys(gmvEngagement.focusProducts || {});\n"
    "  const caM1   = gmvCaPerClientPeriod(ENG_PERIOD_M1);\n"
    "  const caM2   = gmvCaPerClientPeriod(ENG_PERIOD_M2);\n"
    "  const fmt    = n => Math.round(n || 0).toLocaleString('en-US');\n"
    "  const palierOpts = ['<option value=\"0\">' + engT('pal_no_target') + '</option>'].concat(\n"
    "    gmvEngagement.paliers.map(p => `<option value=\"${p.palier}\">${engT('pal_lvl', { n: p.palier })} (${fmt(p.threshold)} MAD)</option>`)\n"
    "  ).join('');\n"
    "  let cardsHtml = '';\n"
    "  myPhones.forEach(phone => {\n"
    "    const cl       = (gmv.clients || {})[phone] || {};\n"
    "    const target   = palTgts[phone] || 0;\n"
    "    const targetP  = (gmvEngagement.paliers || []).find(p => p.palier === parseInt(target));\n"
    "    const cM1      = caM1[phone] || 0;\n"
    "    const cBoth    = (caM1[phone] || 0) + (caM2[phone] || 0);\n"
    "    const ach      = gmvAchievedPalier(cBoth);\n"
    "    // Per-client product commits + milestone achievement counts.\n"
    "    const myProds  = Object.keys(cFocus[phone] || {}).filter(c => cFocus[phone][c] && cFocus[phone][c].selected);\n"
    "    const m1Count  = gmvClientAchievedM1(seller, phone, myProds);\n"
    "    const bothCount = gmvClientAchievedBoth(seller, phone, myProds);\n"
    "    const m1HitMileMile = m1Count   >= ENG_CLIENT_MILESTONE_M1;\n"
    "    const bHitMile      = bothCount >= ENG_CLIENT_MILESTONE_BOTH;\n"
    "    // Gift unlock = milestone met AND client GMV crossed the targeted palier.\n"
    "    const m1Open   = !!(targetP && cM1   >= (targetP.threshold || 0) && m1HitMileMile);\n"
    "    const bothOpen = !!(targetP && cBoth >= (targetP.threshold || 0) && bHitMile);\n"
    "    const m1Pct    = Math.min(100, Math.round((m1Count   / ENG_CLIENT_MILESTONE_M1)   * 100));\n"
    "    const bothPct  = Math.min(100, Math.round((bothCount / ENG_CLIENT_MILESTONE_BOTH) * 100));\n"
    "    const prodPct  = Math.min(100, Math.round((myProds.length / ENG_CLIENT_MIN_PRODUCTS) * 100));\n"
    "    const prodOk   = myProds.length >= ENG_CLIENT_MIN_PRODUCTS;\n"
    "    const giftRow = (label, count, total, pct, open, gmvCur, gmvTgt) => `\n"
    "      <div style=\"display:flex; justify-content:space-between; align-items:center; gap:10px; padding:10px 12px; background:${open ? '#f0fdf4' : '#f8fafc'}; border:1px solid ${open ? '#86efac' : '#e2e8f0'}; border-radius:8px; margin-top:8px;\">\n"
    "        <div style=\"flex:1; min-width:0;\">\n"
    "          <div style=\"display:flex; align-items:center; gap:6px; font-size:12.5px; font-weight:600; color:#0f172a;\">\n"
    "            <span>${label}</span>\n"
    "            <span style=\"font-size:11px; font-weight:600; color:${open ? '#16a34a' : '#94a3b8'};\">${open ? '🎁 ' + engT('pal_gift_open') : engT('pal_gift_locked')}</span>\n"
    "          </div>\n"
    "          <div style=\"display:flex; gap:10px; flex-wrap:wrap; font-size:11px; color:#64748b; margin-top:4px;\">\n"
    "            <span><b style=\"color:${count >= total ? '#16a34a' : '#0f172a'};\">${count}</b> / ${total} ${engT('pal_products')}</span>\n"
    "            ${gmvTgt ? `<span><b style=\"color:${gmvCur >= gmvTgt ? '#16a34a' : '#0f172a'};\">${fmt(gmvCur)}</b> / ${fmt(gmvTgt)} MAD</span>` : `<span style=\"color:#dc2626;\">${engT('pal_no_target_set')}</span>`}\n"
    "          </div>\n"
    "          <div style=\"height:4px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:6px;\">\n"
    "            <div style=\"height:100%; width:${pct}%; background:${open ? '#16a34a' : '#3b82f6'}; transition:width .4s;\"></div>\n"
    "          </div>\n"
    "        </div>\n"
    "      </div>`;\n"
    "    cardsHtml += `\n"
    "      <div class=\"pal-card\" style=\"background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:14px; margin-bottom:12px;\">\n"
    "        <div style=\"display:flex; justify-content:space-between; align-items:flex-start; gap:8px; flex-wrap:wrap;\">\n"
    "          <div style=\"min-width:0; flex:1;\">\n"
    "            <div style=\"font-weight:700; font-size:15px; color:#0f172a; line-height:1.2;\">${gmvEscapeHtmlEng(cl.name || '(no name)')}</div>\n"
    "            <div style=\"font-family:monospace; font-size:11px; color:#94a3b8; margin-top:2px;\">${gmvEscapeHtmlEng(phone)}</div>\n"
    "          </div>\n"
    "          ${ach ? `<span style=\"background:#dbeafe; color:#1e40af; padding:3px 10px; border-radius:99px; font-size:11px; font-weight:600; white-space:nowrap;\">${engT('pal_achieved')} ${ach.palier}</span>` : ''}\n"
    "        </div>\n"
    "        <div style=\"margin-top:12px; padding-top:10px; border-top:1px solid #f1f5f9; display:flex; align-items:center; gap:10px; font-size:12px;\">\n"
    "          <span style=\"color:#64748b; flex-shrink:0;\">${engT('pal_target')} :</span>\n"
    "          <select data-eng-palier=\"${gmvEscapeHtmlEng(phone)}\" style=\"flex:1; padding:6px 8px; border:1px solid #cbd5e1; border-radius:6px; font-size:12px; background:#fff;\">\n"
    "            ${palierOpts.replace('value=\"' + target + '\"', 'value=\"' + target + '\" selected')}\n"
    "          </select>\n"
    "        </div>\n"
    "        <div style=\"margin-top:10px; padding-top:10px; border-top:1px solid #f1f5f9;\">\n"
    "          <div style=\"display:flex; justify-content:space-between; align-items:center; font-size:12px;\">\n"
    "            <span style=\"color:#64748b;\">${engT('pal_my_products')} : <b style=\"color:${prodOk ? '#16a34a' : '#dc2626'};\">${myProds.length}</b><span style=\"color:#94a3b8;\"> / ${ENG_CLIENT_MIN_PRODUCTS}</span></span>\n"
    "            <button type=\"button\" data-pal-edit=\"${gmvEscapeHtmlEng(phone)}\" style=\"background:#0f172a; border:0; color:#fff; padding:5px 12px; border-radius:6px; font-size:11px; font-weight:600; cursor:pointer;\">${engT('pal_edit')}</button>\n"
    "          </div>\n"
    "          <div style=\"height:4px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:6px;\">\n"
    "            <div style=\"height:100%; width:${prodPct}%; background:${prodOk ? '#16a34a' : '#3b82f6'}; transition:width .4s;\"></div>\n"
    "          </div>\n"
    "          <div data-pal-products=\"${gmvEscapeHtmlEng(phone)}\" style=\"display:none; margin-top:10px; max-height:240px; overflow-y:auto; padding:8px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px;\">\n"
    "            ${focusCodes.length ? focusCodes.map(code => {\n"
    "              const meta = gmvEngagement.focusProducts[code] || {};\n"
    "              const checked = !!(cFocus[phone] && cFocus[phone][code] && cFocus[phone][code].selected);\n"
    "              const nm = (meta.name || '').slice(0, 40);\n"
    "              return `<label style=\"display:flex; align-items:center; gap:8px; padding:5px 4px; font-size:12px; cursor:pointer; border-radius:4px;\">\n"
    "                <input type=\"checkbox\" data-pal-prod=\"${gmvEscapeHtmlEng(phone)}\" value=\"${gmvEscapeHtmlEng(code)}\" ${checked ? 'checked' : ''} style=\"cursor:pointer; flex-shrink:0;\">\n"
    "                <span style=\"flex:1; min-width:0; color:#0f172a;\"><b>${gmvEscapeHtmlEng(code)}</b>${nm ? ' — ' + gmvEscapeHtmlEng(nm) : ''}</span>\n"
    "                <span style=\"color:#94a3b8; font-size:11px; flex-shrink:0;\">${engT('eng_ref_min')} ${meta.min || 0}</span>\n"
    "              </label>`;\n"
    "            }).join('') : `<div style=\"color:#94a3b8; font-size:12px; padding:6px;\">${engT('eng_no_focus')}</div>`}\n"
    "          </div>\n"
    "        </div>\n"
    "        ${giftRow(engT('pal_may_gift'),  m1Count,   ENG_CLIENT_MILESTONE_M1,   m1Pct,   m1Open,   cM1,   targetP ? targetP.threshold : 0)}\n"
    "        ${giftRow(engT('pal_both_gift'), bothCount, ENG_CLIENT_MILESTONE_BOTH, bothPct, bothOpen, cBoth, targetP ? targetP.threshold : 0)}\n"
    "      </div>`;\n"
    "  });\n"
    "  panel.innerHTML = `\n"
    "    <div style=\"display:flex; gap:8px; align-items:center; margin:0 0 12px;\">\n"
    "      <span style=\"font-size:13px;\">${myPhones.length} ${engT('pal_clients')}</span>\n"
    "      <button type=\"button\" id=\"engSavePaliers\" class=\"btn btn-primary\" style=\"margin-left:auto; font-size:12px; padding:8px 14px; background:#0f172a; color:#fff; border:0; border-radius:8px; font-weight:600; cursor:pointer;\">${engT('eng_save')}</button>\n"
    "    </div>\n"
    "    ${cardsHtml}`;\n"
    "  // Wire expand toggles for the per-client product list.\n"
    "  panel.querySelectorAll('[data-pal-edit]').forEach(btn => {\n"
    "    btn.addEventListener('click', () => {\n"
    "      const phone = btn.dataset.palEdit;\n"
    "      const list = panel.querySelector('[data-pal-products=\"' + (window.CSS && CSS.escape ? CSS.escape(phone) : phone.replace(/\"/g, '\\\\\"')) + '\"]');\n"
    "      if (list) list.style.display = list.style.display === 'none' ? '' : 'none';\n"
    "    });\n"
    "  });\n"
    "  // Save: collect palier targets + per-client product commits.\n"
    "  const saveBtn = document.getElementById('engSavePaliers');\n"
    "  if (saveBtn) saveBtn.addEventListener('click', async () => {\n"
    "    const paliers = {};\n"
    "    panel.querySelectorAll('[data-eng-palier]').forEach(s => {\n"
    "      const v = parseInt(s.value); if (v > 0) paliers[s.dataset.engPalier] = v;\n"
    "    });\n"
    "    const cFocusOut = {};\n"
    "    panel.querySelectorAll('[data-pal-prod]:checked').forEach(cb => {\n"
    "      const phone = cb.dataset.palProd;\n"
    "      const code  = cb.value;\n"
    "      if (!cFocusOut[phone]) cFocusOut[phone] = {};\n"
    "      cFocusOut[phone][code] = { selected: true };\n"
    "    });\n"
    "    try {\n"
    "      await gmvSaveEngagementCommitment(seller, period, { paliers, clientFocus: cFocusOut });\n"
    "      gmvRenderEngagementPaliers(panel, mySeller, isCreator);\n"
    "      try { saveBtn.textContent = engT('eng_saved'); setTimeout(() => { try { saveBtn.textContent = engT('eng_save'); } catch (_) {} }, 1500); } catch (_) {}\n"
    "    } catch (e) { alert('Save failed: ' + (e.message || e)); }\n"
    "  });\n"
    "}\n"
)


# ---- Patch 5: Add i18n keys for the per-client gift UI -----------------
# We add keys by appending to each language's i18n object right before
# the closing brace.
I18N_FR_OLD = "    sc_great: 'Excellent !', sc_good: 'Bonne progression', sc_keep: 'Continuez',\n"
I18N_FR_NEW = (
    "    sc_great: 'Excellent !', sc_good: 'Bonne progression', sc_keep: 'Continuez',\n"
    "    pal_target: 'Palier ciblé', pal_my_products: 'Mes produits engagés',\n"
    "    pal_edit: 'Modifier', pal_done: 'Fermer',\n"
    "    pal_no_target: '— Pas de palier ciblé —', pal_no_target_set: 'Pas de palier ciblé',\n"
    "    pal_lvl: 'Palier {n}', pal_achieved: 'Palier atteint',\n"
    "    pal_clients: 'client(s) revendiqué(s)', pal_no_clients: 'Aucun client revendiqué. Allez dans \\\"Mes clients\\\" pour en revendiquer.',\n"
    "    pal_no_paliers: 'Aucun palier défini. Demandez au créateur de téléverser le fichier.',\n"
    "    pal_may_gift: 'Cadeau Mai 2026', pal_both_gift: 'Cadeau Mai+Juin 2026',\n"
    "    pal_gift_open: 'Cadeau débloqué', pal_gift_locked: 'Verrouillé',\n"
    "    pal_products: 'produits',\n"
)
I18N_EN_OLD = "    sc_great: 'Excellent!', sc_good: 'Good progress', sc_keep: 'Keep going',\n"
I18N_EN_NEW = (
    "    sc_great: 'Excellent!', sc_good: 'Good progress', sc_keep: 'Keep going',\n"
    "    pal_target: 'Target palier', pal_my_products: 'My committed products',\n"
    "    pal_edit: 'Edit', pal_done: 'Close',\n"
    "    pal_no_target: '— No target —', pal_no_target_set: 'No target set',\n"
    "    pal_lvl: 'Palier {n}', pal_achieved: 'Reached palier',\n"
    "    pal_clients: 'claimed client(s)', pal_no_clients: 'No claimed clients. Go to \\\"My clients\\\" to claim some.',\n"
    "    pal_no_paliers: 'No paliers defined. Ask the creator to upload the paliers file.',\n"
    "    pal_may_gift: 'May 2026 gift', pal_both_gift: 'May+June 2026 gift',\n"
    "    pal_gift_open: 'Gift unlocked', pal_gift_locked: 'Locked',\n"
    "    pal_products: 'products',\n"
)
I18N_AR_OLD = "    sc_great: '🔥 ممتاز !', sc_good: 'تقدم جيد', sc_keep: 'واصل',\n"
I18N_AR_NEW = (
    "    sc_great: '🔥 ممتاز !', sc_good: 'تقدم جيد', sc_keep: 'واصل',\n"
    "    pal_target: 'المستوى المستهدف', pal_my_products: 'منتجاتي الملتزم بها',\n"
    "    pal_edit: 'تعديل', pal_done: 'إغلاق',\n"
    "    pal_no_target: '— لا يوجد مستوى مستهدف —', pal_no_target_set: 'لم يتم تحديد مستوى',\n"
    "    pal_lvl: 'مستوى {n}', pal_achieved: 'تم بلوغ المستوى',\n"
    "    pal_clients: 'زبون مرتبط', pal_no_clients: 'لا يوجد زبون مرتبط. ادهب إلى \\\"زبنائي\\\" لاختيارهم.',\n"
    "    pal_no_paliers: 'لا توجد مستويات. اطلب من المالك رفع الملف.',\n"
    "    pal_may_gift: 'هدية ماي 2026', pal_both_gift: 'هدية ماي+يونيو 2026',\n"
    "    pal_gift_open: 'الهدية مفتوحة', pal_gift_locked: 'مغلقة',\n"
    "    pal_products: 'منتجات',\n"
)


def main():
    print('Patching: ' + INDEX_PATH)
    src = read_file(INDEX_PATH)
    nl = '\r\n' if '\r\n' in src else '\n'

    src, _ = replace_once(src, OLD_LOAD,    NEW_LOAD,    'gmvLoadEngagement extracts __byClient', nl)
    src, _ = replace_once(src, OLD_SAVE,    NEW_SAVE,    'gmvSaveEngagementCommitment merges clientFocus', nl)
    src, _ = replace_once(src, HELPERS_ANCHOR, HELPERS_NEW, 'add per-client engagement helpers', nl)
    src, _ = replace_once(src, OLD_PALIERS, NEW_PALIERS, 'rewrite gmvRenderEngagementPaliers (cards + per-client products)', nl)
    src, _ = replace_once(src, I18N_FR_OLD, I18N_FR_NEW, 'i18n FR keys for per-client gift', nl)
    src, _ = replace_once(src, I18N_EN_OLD, I18N_EN_NEW, 'i18n EN keys for per-client gift', nl)
    src, _ = replace_once(src, I18N_AR_OLD, I18N_AR_NEW, 'i18n AR keys for per-client gift', nl)

    write_file(INDEX_PATH, src)
    print('Done.')


if __name__ == '__main__':
    main()
    main()
