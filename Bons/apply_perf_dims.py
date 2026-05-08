#!/usr/bin/env python3
"""Replace single scope dropdown with multi-dimension toggle (Seller / Store / Client / Category).

User picks any subset of the 4 dims; the perf table groups rows by that combination.
Targets are looked up only when the chosen combo matches a known target shape.
"""
import os, sys
TARGET = r"C:\Users\KamalSAGUEM\OneDrive - Beyond believers\Bureau\Rehab app ( planner) - Copie\rigab_app\index.html"

def must_replace_once(src, anchor, replacement, label):
    n = src.count(anchor)
    if n == 0: raise SystemExit("[FAIL] anchor not found for " + label)
    if n > 1:  raise SystemExit("[FAIL] anchor appears " + str(n) + "x for " + label)
    return src.replace(anchor, replacement, 1)

def main():
    with open(TARGET, 'r', encoding='utf-8') as f:
        src = f.read()
    if "GMV_PERF_DIMS" in src:
        print("[skip] already done"); return

    # Replace the entire body of gmvComputePerf + gmvRenderFlatPerformance with the dim-based version.
    # Anchor: from "function gmvComputePerf(scope, filters) {" through end of gmvOpenPerfFltPopover.
    # That's hard. Instead, surgically replace gmvComputePerf and gmvRenderFlatPerformance.

    # 1) Replace gmvComputePerf signature + body
    old_compute_start = "function gmvComputePerf(scope, filters) {\n"
    if old_compute_start not in src:
        raise SystemExit("[FAIL] gmvComputePerf not found")
    # Find end: the matching closing "}\n\n" before "const GMV_PERF_SCOPES"
    start = src.index(old_compute_start)
    end_marker = "const GMV_PERF_SCOPES"
    end = src.index(end_marker)
    old_compute_block = src[start:end]
    new_compute_block = (
        "const GMV_PERF_DIMS = [\n"
        "  { id: 'seller',   label: 'Seller',   col: 'Seller'   },\n"
        "  { id: 'store',    label: 'Store',    col: 'Store'    },\n"
        "  { id: 'client',   label: 'Client',   col: 'Client'   },\n"
        "  { id: 'category', label: 'Category', col: 'Category' }\n"
        "];\n"
        "\n"
        "function gmvPerfValueFor(dim, o) {\n"
        "  if (dim === 'seller')   return (gmv.clients[o.phone] && gmv.clients[o.phone].seller) || '(no seller)';\n"
        "  if (dim === 'store')    return o.store || '(no store)';\n"
        "  if (dim === 'client')   return o.phone;\n"
        "  if (dim === 'category') { const e = (gmv.productCategories || {})[o.productCode || '']; return (e && e.category) || '(uncategorized)'; }\n"
        "  return '';\n"
        "}\n"
        "\n"
        "function gmvPerfRenderDim(dim, value) {\n"
        "  if (dim === 'client') return gmvDisplayName(value);\n"
        "  return value;\n"
        "}\n"
        "\n"
        "function gmvComputePerf(dims, filters) {\n"
        "  const fromMs = gmv.dateFrom ? new Date(gmv.dateFrom + 'T00:00:00').getTime() : -Infinity;\n"
        "  const toMs   = gmv.dateTo   ? new Date(gmv.dateTo   + 'T23:59:59').getTime() :  Infinity;\n"
        "  const sellersSet = new Set((filters && filters.sellers) || []);\n"
        "  const storesSet  = new Set((filters && filters.stores)  || []);\n"
        "  const clientsSet = new Set((filters && filters.clients) || []);\n"
        "  const catsSet    = new Set((filters && filters.categories) || []);\n"
        "  const rollup = {};\n"
        "  (gmv.orders || []).forEach(o => {\n"
        "    if (!o.phone || !gmv.clients[o.phone]) return;\n"
        "    if (!o.status || GMV_STATUSES.indexOf(o.status) < 0) return;\n"
        "    if (o.status !== 'PENDING') {\n"
        "      const t = o.date ? o.date.getTime() : 0;\n"
        "      if (t < fromMs || t > toMs) return;\n"
        "    }\n"
        "    const seller = gmv.clients[o.phone].seller || '(no seller)';\n"
        "    const store  = o.store || '(no store)';\n"
        "    const ent = (gmv.productCategories || {})[o.productCode || ''];\n"
        "    const category = (ent && ent.category) ? ent.category : '(uncategorized)';\n"
        "    if (sellersSet.size && !sellersSet.has(seller))   return;\n"
        "    if (storesSet.size  && !storesSet.has(store))     return;\n"
        "    if (clientsSet.size && !clientsSet.has(o.phone))  return;\n"
        "    if (catsSet.size    && !catsSet.has(category))    return;\n"
        "    const vals = dims.map(d => gmvPerfValueFor(d, o));\n"
        "    const key = vals.join('\\u0001');\n"
        "    if (!rollup[key]) rollup[key] = { dims: dims.slice(), vals: vals, status: {} };\n"
        "    rollup[key].status[o.status] = (rollup[key].status[o.status] || 0) + o.amount;\n"
        "  });\n"
        "  return rollup;\n"
        "}\n"
        "\n"
    )
    src = src.replace(old_compute_block, new_compute_block)

    # 2) Replace GMV_PERF_SCOPES const + gmvRenderFlatPerformance body up to gmvWireFlatPerfHandlers
    old_scopes_start = "const GMV_PERF_SCOPES = [\n"
    if old_scopes_start not in src:
        raise SystemExit("[FAIL] GMV_PERF_SCOPES not found")
    start2 = src.index(old_scopes_start)
    end2_marker = "function gmvWireFlatPerfHandlers"
    end2 = src.index(end2_marker)
    old_block2 = src[start2:end2]
    new_block2 = (
        "function gmvRenderFlatPerformance(wrap) {\n"
        "  if (!gmv.perfFilters) gmv.perfFilters = { sellers: [], stores: [], clients: [], categories: [], search: '' };\n"
        "  if (!gmv.perfDims) {\n"
        "    try {\n"
        "      const stored = loadJSON('rihab_gmv_perfdims_v1');\n"
        "      gmv.perfDims = (Array.isArray(stored) && stored.length) ? stored : ['seller'];\n"
        "    } catch (_) { gmv.perfDims = ['seller']; }\n"
        "  }\n"
        "  if (!gmv.perfLimit) gmv.perfLimit = 50;\n"
        "  const dims = gmv.perfDims;\n"
        "  const filters = gmv.perfFilters;\n"
        "  const rollup = gmvComputePerf(dims, filters);\n"
        "  let rows = Object.values(rollup);\n"
        "  const q = (filters.search || '').trim().toLowerCase();\n"
        "  if (q) rows = rows.filter(r => r.vals.some((v, i) => (gmvPerfRenderDim(r.dims[i], v) || '').toLowerCase().includes(q)));\n"
        "  rows.sort((a, b) => ((b.status['DELIVERED']||0) - (a.status['DELIVERED']||0)) || a.vals.join().localeCompare(b.vals.join()));\n"
        "  const dimToggle = (d) => {\n"
        "    const active = dims.indexOf(d.id) >= 0;\n"
        "    return '<button type=\"button\" data-perf-dim=\"' + d.id + '\" style=\"padding:6px 12px; border-radius:6px; border:1px solid var(--border); background:' + (active?'var(--accent, #0f172a)':'transparent') + '; color:' + (active?'#fff':'inherit') + '; cursor:pointer; font-size:12px; font-weight:600;\">' + (active?'\\u2713 ':'+ ') + d.label + '</button>';\n"
        "  };\n"
        "  const dimsBar = '<div style=\"display:flex; gap:6px; margin-bottom:10px; flex-wrap:wrap; align-items:center;\"><span style=\"font-size:11px; color:var(--text-soft); font-weight:600; text-transform:uppercase; letter-spacing:0.06em;\">Group by:</span>' + GMV_PERF_DIMS.map(dimToggle).join('') + (dims.length === 0 ? '<span style=\"color:var(--danger); font-size:12px;\">pick at least one</span>' : '') + '</div>';\n"
        "  const chip = (kind, label) => {\n"
        "    const n = (filters[kind] || []).length;\n"
        "    return '<button type=\"button\" class=\"gmv-flt-chip' + (n ? ' has-selection' : '') + '\" data-perf-flt-kind=\"' + kind + '\">' +\n"
        "      '<span>' + label + '</span>' +\n"
        "      (n ? '<span class=\"chip-count\">' + n + '</span>' : '<span style=\"color:var(--text-soft);font-size:11px;\">All</span>') +\n"
        "    '</button>';\n"
        "  };\n"
        "  const hasAny = (filters.sellers||[]).length || (filters.stores||[]).length || (filters.clients||[]).length || (filters.categories||[]).length || (filters.search && filters.search.trim());\n"
        "  let html = dimsBar + '<div class=\"gmv-flt-bar\">' +\n"
        "    '<input type=\"text\" class=\"gmv-flt-search\" id=\"gmvPerfSearch\" placeholder=\"Search...\" value=\"' + escapeHtml(filters.search || '') + '\">' +\n"
        "    chip('sellers', 'Sellers') + chip('stores', 'Stores') + chip('clients', 'Clients') + chip('categories', 'Categories') +\n"
        "    (hasAny ? '<button type=\"button\" class=\"gmv-flt-clear\" id=\"gmvPerfClear\">\\u2715 Clear filters</button>' : '') +\n"
        "    '<span class=\"gmv-flt-count\">' + rows.length + ' rows</span>' +\n"
        "  '</div>';\n"
        "  if (!dims.length) {\n"
        "    html += '<div class=\"gmv-empty\"><div class=\"gmv-empty-icon\">\\u26A0</div>Pick at least one dimension above.</div>';\n"
        "    wrap.innerHTML = html; gmvWireFlatPerfHandlers(wrap); return;\n"
        "  }\n"
        "  if (!rows.length) {\n"
        "    html += '<div class=\"gmv-empty\"><div class=\"gmv-empty-icon\">\\u26A0</div>No data matches your filters.</div>';\n"
        "    wrap.innerHTML = html; gmvWireFlatPerfHandlers(wrap); return;\n"
        "  }\n"
        "  const limit = gmv.perfLimit || 50;\n"
        "  const visible = rows.slice(0, limit);\n"
        "  const hidden = Math.max(0, rows.length - visible.length);\n"
        "  const bucket = gmvActivePeriodBucket();\n"
        "  // Target lookup only for known shapes; else 0.\n"
        "  const targetForRow = (vals) => {\n"
        "    const sig = dims.slice().sort().join(',');\n"
        "    const get = (id) => vals[dims.indexOf(id)];\n"
        "    if (sig === 'seller')   return bucket.sellers[get('seller')] || 0;\n"
        "    if (sig === 'store')    return bucket.stores[get('store')] || 0;\n"
        "    if (sig === 'client')   return bucket.clients[get('client')] || 0;\n"
        "    if (sig === 'category') return (bucket.categories || {})[get('category')] || 0;\n"
        "    if (sig === 'seller,store')   return ((bucket.storesBySeller || {})[get('seller')] || {})[get('store')] || 0;\n"
        "    if (sig === 'client,store')   return ((bucket.storesByClient || {})[get('client')] || {})[get('store')] || 0;\n"
        "    if (sig === 'category,store') return ((bucket.categoriesByStore || {})[get('store')] || {})[get('category')] || 0;\n"
        "    return 0;\n"
        "  };\n"
        "  let table = '<div class=\"gmv-table-wrap\"><table class=\"gmv-table\"><thead><tr>';\n"
        "  dims.forEach(d => {\n"
        "    const def = GMV_PERF_DIMS.find(x => x.id === d);\n"
        "    table += '<th>' + (def ? def.col : d) + '</th>';\n"
        "  });\n"
        "  table += '<th class=\"num\">Delivered</th><th class=\"num\">Target</th><th>Progress</th><th class=\"num\" style=\"width:54px;\">%</th>';\n"
        "  GMV_STATUSES.filter(s => s !== 'DELIVERED').forEach(s => {\n"
        "    const lbl = s.replace(/_/g, ' ').toLowerCase().replace(/\\b\\w/g, c => c.toUpperCase());\n"
        "    table += '<th class=\"num\" title=\"' + s + '\">' + lbl + '</th>';\n"
        "  });\n"
        "  table += '</tr></thead><tbody>';\n"
        "  visible.forEach(r => {\n"
        "    const delivered = r.status['DELIVERED'] || 0;\n"
        "    const target = targetForRow(r.vals);\n"
        "    let bulletHtml, pctTxt;\n"
        "    if (target > 0) {\n"
        "      const scaleMax = target / 0.75;\n"
        "      const fillPct = Math.max(0, Math.min(100, (delivered / scaleMax) * 100));\n"
        "      const ok = delivered >= target;\n"
        "      bulletHtml = '<div class=\"gmv-bullet\" title=\"' + gmvFmtFull(delivered) + ' / ' + gmvFmtFull(target) + ' MAD\"><div class=\"gmv-bullet-fill ' + (ok ? 'ok' : 'partial') + '\" style=\"width:' + fillPct + '%;\"></div><div class=\"gmv-bullet-tick\" style=\"left:75%;\"></div></div>';\n"
        "      pctTxt = Math.round((delivered / target) * 100) + '%';\n"
        "    } else {\n"
        "      bulletHtml = '<span style=\"font-size:11px; color:var(--text-soft);\">no target</span>';\n"
        "      pctTxt = '<span class=\"muted-num\">0%</span>';\n"
        "    }\n"
        "    table += '<tr class=\"gmv-row-seller\">';\n"
        "    r.vals.forEach((v, i) => {\n"
        "      const rendered = gmvPerfRenderDim(r.dims[i], v);\n"
        "      const meta = r.dims[i] === 'client' ? '<div class=\"gmv-seller-meta\">' + escapeHtml(v) + '</div>' : '';\n"
        "      table += '<td><div class=\"gmv-seller-name\">' + escapeHtml(rendered) + '</div>' + meta + '</td>';\n"
        "    });\n"
        "    table += '<td class=\"num\" title=\"' + gmvFmtFull(delivered) + ' MAD\">' + gmvFmtCompact(delivered) + '</td>';\n"
        "    table += '<td class=\"num' + (target > 0 ? '' : ' muted-num') + '\">' + (target > 0 ? gmvFmtCompact(target) : '\\u2014') + '</td>';\n"
        "    table += '<td>' + bulletHtml + '</td>';\n"
        "    table += '<td class=\"num\">' + pctTxt + '</td>';\n"
        "    GMV_STATUSES.filter(s => s !== 'DELIVERED').forEach(s => {\n"
        "      const v = r.status[s] || 0;\n"
        "      table += '<td class=\"num' + (v > 0 ? '' : ' muted-num') + '\" title=\"' + gmvFmtFull(v) + ' MAD\">' + (v > 0 ? gmvFmtCompact(v) : '0') + '</td>';\n"
        "    });\n"
        "    table += '</tr>';\n"
        "  });\n"
        "  const colCount = dims.length + 4 + GMV_STATUSES.length - 1;\n"
        "  table += '</tbody>';\n"
        "  if (hidden > 0) {\n"
        "    table += '<tfoot><tr><td colspan=\"' + colCount + '\"><button type=\"button\" class=\"gmv-showmore-btn\" id=\"gmvPerfShowMore\">Show more <span class=\"gmv-showmore-count\">+' + Math.min(50, hidden) + ' (' + hidden + ' hidden)</span></button></td></tr></tfoot>';\n"
        "  }\n"
        "  table += '</table></div>';\n"
        "  html += table;\n"
        "  wrap.innerHTML = html;\n"
        "  gmvWireFlatPerfHandlers(wrap);\n"
        "}\n"
        "\n"
    )
    src = src.replace(old_block2, new_block2)

    # 3) Update gmvWireFlatPerfHandlers to wire dim toggles instead of scope dropdown
    old_wire_scope = (
        "  const sel = wrap.querySelector('#gmvPerfScope');\n"
        "  if (sel) sel.addEventListener('change', () => {\n"
        "    gmv.perfScope = sel.value; gmv.perfLimit = 50;\n"
        "    try { saveJSON('rihab_gmv_perfscope_v1', gmv.perfScope); } catch (_) {}\n"
        "    gmvRenderResults();\n"
        "  });"
    )
    new_wire_dims = (
        "  wrap.querySelectorAll('button[data-perf-dim]').forEach(btn => {\n"
        "    btn.addEventListener('click', () => {\n"
        "      const id = btn.dataset.perfDim;\n"
        "      if (!Array.isArray(gmv.perfDims)) gmv.perfDims = [];\n"
        "      const i = gmv.perfDims.indexOf(id);\n"
        "      if (i >= 0) gmv.perfDims.splice(i, 1);\n"
        "      else gmv.perfDims.push(id);\n"
        "      gmv.perfLimit = 50;\n"
        "      try { saveJSON('rihab_gmv_perfdims_v1', gmv.perfDims); } catch (_) {}\n"
        "      gmvRenderResults();\n"
        "    });\n"
        "  });"
    )
    src = src.replace(old_wire_scope, new_wire_dims)

    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] Performance now has multi-dim group-by (Seller / Store / Client / Category) + filters.")

if __name__ == '__main__':
    main()
