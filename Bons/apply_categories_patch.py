#!/usr/bin/env python3
"""
One-shot patch: adds the Product Categories upload + Performance by Category
to the GMV Tracker in:
  C:\\Users\\KamalSAGUEM\\OneDrive - Beyond believers\\Bureau\\Rehab app ( planner) - Copie\\rigab_app\\index.html

Run once. Idempotent: re-running it on an already-patched file is a no-op
(every block has an "already patched?" guard).

Usage (Windows PowerShell, from anywhere):
    python "C:\\Users\\KamalSAGUEM\\OneDrive - Beyond believers\\Bureau\\Rehab app ( planner)\\Bons\\apply_categories_patch.py"
"""

import sys, os

TARGET = r"C:\Users\KamalSAGUEM\OneDrive - Beyond believers\Bureau\Rehab app ( planner) - Copie\rigab_app\index.html"

def must_replace_once(src, anchor, replacement, label):
    n = src.count(anchor)
    if n == 0:
        raise SystemExit("[FAIL] anchor not found for " + label + "\n  anchor was:\n  " + repr(anchor[:120]))
    if n > 1:
        raise SystemExit("[FAIL] anchor appears " + str(n) + "x for " + label + " (expected unique)")
    return src.replace(anchor, replacement, 1)

def apply_patch(path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    original_len = len(src)
    changed = False

    # ---------- A: LS key constant ----------
    if "GMV_LS_CATEGORIES" not in src:
        src = must_replace_once(
            src,
            "const GMV_LS_NAMES   = 'rihab_gmv_names_v1';",
            "const GMV_LS_NAMES   = 'rihab_gmv_names_v1';\nconst GMV_LS_CATEGORIES = 'rihab_gmv_categories_v1';",
            "A: LS key"
        )
        changed = True
        print("[OK] A: LS key constant added")
    else:
        print("[skip] A already applied")

    # ---------- B: gmv state field ----------
    if "productCategories:" not in src:
        src = must_replace_once(
            src,
            "  clientsByRetailerId: {}, // retailerId -> canonical phone",
            "  clientsByRetailerId: {}, // retailerId -> canonical phone\n  productCategories: {}, // productCode -> { description, category }",
            "B: state field"
        )
        changed = True
        print("[OK] B: state field added")
    else:
        print("[skip] B already applied")

    # ---------- C: restore from localStorage on init ----------
    if "GMV_LS_CATEGORIES" in src and "loadJSON(GMV_LS_CATEGORIES)" not in src:
        src = must_replace_once(
            src,
            "    const savedNames = loadJSON(GMV_LS_NAMES);\n    if (savedNames && typeof savedNames === 'object') gmv.namesByPhone = savedNames;",
            "    const savedNames = loadJSON(GMV_LS_NAMES);\n    if (savedNames && typeof savedNames === 'object') gmv.namesByPhone = savedNames;\n    const savedCats = loadJSON(GMV_LS_CATEGORIES);\n    if (savedCats && typeof savedCats === 'object') gmv.productCategories = savedCats;",
            "C: restore on init"
        )
        changed = True
        print("[OK] C: localStorage restore added")
    else:
        print("[skip] C already applied")

    # ---------- D: Supabase push function for categories ----------
    if "gmvPushCategoriesToSupabase" not in src:
        new_fn = (
            "async function gmvPushCategoriesToSupabase() {\n"
            "  if (!sbUser || typeof sbWriteKey !== 'function') return false;\n"
            "  try {\n"
            "    return await sbWriteKey('gmv_categories', gmv.productCategories || {});\n"
            "  } catch (e) {\n"
            "    console.warn('gmv push categories to supabase failed:', e);\n"
            "    return false;\n"
            "  }\n"
            "}\n"
            "\n"
            "// Pull product categories from Supabase when local cache is empty.\n"
            "async function gmvPullCategoriesFromSupabaseIfNeeded() {\n"
            "  if (gmv.productCategories && Object.keys(gmv.productCategories).length) return;\n"
            "  if (!sbUser || typeof sbReadKey !== 'function') return;\n"
            "  try {\n"
            "    const cloudCats = await sbReadKey('gmv_categories');\n"
            "    if (cloudCats && typeof cloudCats === 'object') {\n"
            "      gmv.productCategories = cloudCats;\n"
            "      try { saveJSON(GMV_LS_CATEGORIES, cloudCats); } catch (_) {}\n"
            "    }\n"
            "  } catch (e) { console.warn('gmv pull categories failed:', e); }\n"
            "}\n"
            "\n"
        )
        src = must_replace_once(
            src,
            "// Pull orders + names from Supabase when local cache is empty. Mirrors\n// gmvPullClientsFromSupabaseIfNeeded.",
            new_fn + "// Pull orders + names from Supabase when local cache is empty. Mirrors\n// gmvPullClientsFromSupabaseIfNeeded.",
            "D: supabase fns"
        )
        changed = True
        print("[OK] D: Supabase push/pull functions added")
    else:
        print("[skip] D already applied")

    # ---------- E: include categories in gmvSyncAllToCloud ----------
    if "tasks.push(gmvPushCategoriesToSupabase())" not in src:
        src = must_replace_once(
            src,
            "  if ((gmv.orders && gmv.orders.length) || (gmv.namesByPhone && Object.keys(gmv.namesByPhone).length)) tasks.push(gmvPushOrdersToSupabase());",
            "  if ((gmv.orders && gmv.orders.length) || (gmv.namesByPhone && Object.keys(gmv.namesByPhone).length)) tasks.push(gmvPushOrdersToSupabase());\n  if (gmv.productCategories && Object.keys(gmv.productCategories).length) tasks.push(gmvPushCategoriesToSupabase());",
            "E: syncAllToCloud"
        )
        changed = True
        print("[OK] E: syncAllToCloud now pushes categories")
    else:
        print("[skip] E already applied")

    # ---------- F: call pull for categories during init ----------
    if "gmvPullCategoriesFromSupabaseIfNeeded" in src and "await gmvPullCategoriesFromSupabaseIfNeeded();" not in src:
        src = must_replace_once(
            src,
            "  await gmvPullOrdersFromSupabaseIfNeeded();\n  await gmvPullRangeFromSupabaseIfNeeded();",
            "  await gmvPullOrdersFromSupabaseIfNeeded();\n  await gmvPullCategoriesFromSupabaseIfNeeded();\n  await gmvPullRangeFromSupabaseIfNeeded();",
            "F: pull on init"
        )
        changed = True
        print("[OK] F: init now pulls categories")
    else:
        print("[skip] F already applied")

    # ---------- G: wire the file input ----------
    if "gmvCategoriesFile" in src and "gmvOnUploadCategories" not in src.split("addEventListener('change'")[0]:
        # second guard: only patch if listener wiring isn't there yet
        pass
    if "gmvOnUploadCategories" not in src:
        src = must_replace_once(
            src,
            "  document.getElementById('gmvOrdersFile')?.addEventListener('change', gmvOnUploadOrders);",
            "  document.getElementById('gmvOrdersFile')?.addEventListener('change', gmvOnUploadOrders);\n  document.getElementById('gmvCategoriesFile')?.addEventListener('change', gmvOnUploadCategories);",
            "G: file input wiring"
        )
        changed = True
        print("[OK] G: file input wired")
    else:
        print("[skip] G already applied")

    # ---------- H: gmvOnUploadCategories handler ----------
    if "async function gmvOnUploadCategories" not in src:
        new_handler = (
            "async function gmvOnUploadCategories(e) {\n"
            "  const f = e.target.files && e.target.files[0]; if (!f) return;\n"
            "  try {\n"
            "    const rows = await readXlsx(f);\n"
            "    if (!rows.length) throw new Error('Empty file.');\n"
            "    const cCode = findCol(rows[0], ['Code','code','partnerCode','PartnerCode','product_code','ProductCode']);\n"
            "    const cDesc = findCol(rows[0], ['Description','description','productName','ProductName','product_name','Name']);\n"
            "    const cCat  = findCol(rows[0], ['Category','category','Categorie','Catégorie']);\n"
            "    if (!cCode) throw new Error('Missing Code column.');\n"
            "    if (!cCat)  throw new Error('Missing Category column.');\n"
            "    let added = 0, skipped = 0;\n"
            "    const map = {};\n"
            "    rows.forEach(r => {\n"
            "      const code = String(r[cCode] || '').trim();\n"
            "      if (!code) { skipped++; return; }\n"
            "      const desc = cDesc ? String(r[cDesc] || '').trim() : '';\n"
            "      const cat  = String(r[cCat] || '').trim() || '(uncategorized)';\n"
            "      map[code] = { description: desc, category: cat };\n"
            "      added++;\n"
            "    });\n"
            "    gmv.productCategories = map;\n"
            "    try { saveJSON(GMV_LS_CATEGORIES, gmv.productCategories); } catch (_) {}\n"
            "    let synced = false;\n"
            "    if (sbUser) synced = await gmvPushCategoriesToSupabase();\n"
            "    const distinctCats = new Set(Object.values(map).map(v => v.category));\n"
            "    const syncSuffix = sbUser\n"
            "      ? (synced ? ' <span style=\"color:var(--success); font-weight:600;\">\\u2713 Synced to your account</span>'\n"
            "                : ' <span style=\"color:var(--warning); font-weight:600;\">\\u26A0 Local only \\u2014 sync to Supabase failed</span>')\n"
            "      : ' <span style=\"color:var(--text-soft);\">\\u2014 Local only (sign in to sync across devices)</span>';\n"
            "    gmvSetSummary('gmvCategoriesSummary',\n"
            "      'Loaded <b>' + added + '</b> product(s) across <b>' + distinctCats.size + '</b> categor' + (distinctCats.size === 1 ? 'y' : 'ies') + '.' +\n"
            "      (skipped ? ' Skipped <b>' + skipped + '</b> with empty Code.' : '') +\n"
            "      syncSuffix);\n"
            "    gmvRenderAll();\n"
            "  } catch (err) {\n"
            "    alert('Categories file error: ' + (err && err.message ? err.message : err));\n"
            "  } finally { try { e.target.value = ''; } catch (_) {} }\n"
            "}\n"
            "\n"
        )
        src = must_replace_once(
            src,
            "async function gmvOnUploadOrders(e) {",
            new_handler + "async function gmvOnUploadOrders(e) {",
            "H: handler"
        )
        changed = True
        print("[OK] H: gmvOnUploadCategories handler added")
    else:
        print("[skip] H already applied")

    # ---------- I: orders upload — capture partnerCode as productCode ----------
    if "const cPartnerCode = findCol(rows[0]" not in src:
        src = must_replace_once(
            src,
            "    const cStoreName = findCol(rows[0], ['storeName','StoreName','store_name','Store name','Store Name']);",
            "    const cStoreName = findCol(rows[0], ['storeName','StoreName','store_name','Store name','Store Name']);\n    const cPartnerCode = findCol(rows[0], ['partnerCode','PartnerCode','partner_code','Code']);",
            "I: orders cPartnerCode lookup"
        )
        changed = True
        print("[OK] I: orders detect partnerCode column")
    else:
        print("[skip] I already applied")

    if "out.push({ phone: np, date: dt, amount: amt, status: st, store: storeRaw, productCode:" not in src:
        src = must_replace_once(
            src,
            "      out.push({ phone: np, date: dt, amount: amt, status: st, store: storeRaw });",
            "      const productCode = cPartnerCode ? String(r[cPartnerCode] || '').trim() : '';\n      out.push({ phone: np, date: dt, amount: amt, status: st, store: storeRaw, productCode: productCode });",
            "I2: push productCode"
        )
        changed = True
        print("[OK] I2: orders rows now carry productCode")
    else:
        print("[skip] I2 already applied")

    # also save productCode in localStorage round-trip
    if "store: o.store || '', productCode:" not in src:
        # Update localStorage save on upload
        src = must_replace_once(
            src,
            "      const ordersForStore = out.map(o => ({ phone: o.phone, date: o.date.toISOString(), amount: o.amount, status: o.status, store: o.store || '' }));",
            "      const ordersForStore = out.map(o => ({ phone: o.phone, date: o.date.toISOString(), amount: o.amount, status: o.status, store: o.store || '', productCode: o.productCode || '' }));",
            "I3: localStorage save productCode"
        )
        # Update Supabase push
        src = must_replace_once(
            src,
            "    const ordersForCloud = (gmv.orders || []).map(o => ({\n      phone: o.phone,\n      date: (o.date && o.date.toISOString) ? o.date.toISOString() : o.date,\n      amount: o.amount,\n      status: o.status,\n      store: o.store || ''\n    }));",
            "    const ordersForCloud = (gmv.orders || []).map(o => ({\n      phone: o.phone,\n      date: (o.date && o.date.toISOString) ? o.date.toISOString() : o.date,\n      amount: o.amount,\n      status: o.status,\n      store: o.store || '',\n      productCode: o.productCode || ''\n    }));",
            "I4: Supabase push productCode"
        )
        # Update restore from localStorage
        src = src.replace(
            "      gmv.orders = savedOrders.map(o => ({\n        phone: o.phone,\n        date: o.date ? new Date(o.date) : null,\n        amount: typeof o.amount === 'number' ? o.amount : parseFloat(o.amount) || 0,\n        status: gmvNormStatus(o.status || ''),\n        store: o.store || ''\n      })).filter(o => o.phone && o.date && o.status && GMV_STATUSES.indexOf(o.status) >= 0);",
            "      gmv.orders = savedOrders.map(o => ({\n        phone: o.phone,\n        date: o.date ? new Date(o.date) : null,\n        amount: typeof o.amount === 'number' ? o.amount : parseFloat(o.amount) || 0,\n        status: gmvNormStatus(o.status || ''),\n        store: o.store || '',\n        productCode: o.productCode || ''\n      })).filter(o => o.phone && o.date && o.status && GMV_STATUSES.indexOf(o.status) >= 0);"
        )
        # Update Supabase pull
        src = src.replace(
            "      gmv.orders = cloudOrders.map(o => ({\n        phone: o.phone,\n        date: o.date ? new Date(o.date) : null,\n        amount: typeof o.amount === 'number' ? o.amount : parseFloat(o.amount) || 0,\n        status: gmvNormStatus(o.status || ''),\n        store: o.store || ''\n      })).filter(o => o.phone && o.date && o.status && GMV_STATUSES.indexOf(o.status) >= 0);",
            "      gmv.orders = cloudOrders.map(o => ({\n        phone: o.phone,\n        date: o.date ? new Date(o.date) : null,\n        amount: typeof o.amount === 'number' ? o.amount : parseFloat(o.amount) || 0,\n        status: gmvNormStatus(o.status || ''),\n        store: o.store || '',\n        productCode: o.productCode || ''\n      })).filter(o => o.phone && o.date && o.status && GMV_STATUSES.indexOf(o.status) >= 0);"
        )
        changed = True
        print("[OK] I3-I4: orders persistence carries productCode end-to-end")
    else:
        print("[skip] I3/I4 already applied")

    # ---------- J: gmvComputeReached — add byCategoryByStatus ----------
    if "byCategoryByStatus" not in src:
        # Add the rollup map declaration
        src = must_replace_once(
            src,
            "  const byStoreByStatus  = {};   // storeName -> { status: amount }\n  const totalByStatus    = {};   // status -> amount",
            "  const byStoreByStatus  = {};   // storeName -> { status: amount }\n  const byCategoryByStatus = {}; // category -> { status: amount }\n  const totalByStatus    = {};   // status -> amount",
            "J1: byCategory map decl"
        )
        # Populate the map per-row (after byStore line)
        src = must_replace_once(
            src,
            "    byStoreByStatus[store][st] = (byStoreByStatus[store][st] || 0) + o.amount;\n    totalByStatus[st] = (totalByStatus[st] || 0) + o.amount;",
            "    byStoreByStatus[store][st] = (byStoreByStatus[store][st] || 0) + o.amount;\n    const _catEntry = (gmv.productCategories || {})[o.productCode || ''];\n    const cat = (_catEntry && _catEntry.category) ? _catEntry.category : '(uncategorized)';\n    if (!byCategoryByStatus[cat]) byCategoryByStatus[cat] = {};\n    byCategoryByStatus[cat][st] = (byCategoryByStatus[cat][st] || 0) + o.amount;\n    totalByStatus[st] = (totalByStatus[st] || 0) + o.amount;",
            "J2: per-row category rollup"
        )
        # Add to the return object
        src = must_replace_once(
            src,
            "    byClientByStatus, bySellerByStatus, byStoreByStatus, totalByStatus,",
            "    byClientByStatus, bySellerByStatus, byStoreByStatus, byCategoryByStatus, totalByStatus,",
            "J3: return byCategoryByStatus"
        )
        changed = True
        print("[OK] J: gmvComputeReached now rolls up by category")
    else:
        print("[skip] J already applied")

    # ---------- K: render Performance by Category fragment ----------
    if "__gmvByCategoryFragment" not in src:
        # Insert the category fragment build right after the byStore fragment.
        # Anchor: the line that closes the byStore block, then append the category block.
        anchor_k = (
            "      window.__gmvByStoreFragment = storeHtml;\n"
            "    } else {\n"
            "      window.__gmvByStoreFragment = '';\n"
            "    }\n"
            "  } else {\n"
            "    window.__gmvByStoreFragment = '';\n"
            "  }"
        )
        replacement_k = (
            "      window.__gmvByStoreFragment = storeHtml;\n"
            "    } else {\n"
            "      window.__gmvByStoreFragment = '';\n"
            "    }\n"
            "    // ----- Performance by Category (Performance page only) -----\n"
            "    const byCategoryByStatus = result.byCategoryByStatus || {};\n"
            "    const cats = Object.keys(byCategoryByStatus);\n"
            "    if (cats.length) {\n"
            "      const niceStatusC = st => st.replace(/_/g, ' ').toLowerCase().replace(/\\b\\w/g, c => c.toUpperCase());\n"
            "      cats.sort((a, b) => ((byCategoryByStatus[b]['DELIVERED'] || 0) - (byCategoryByStatus[a]['DELIVERED'] || 0)) || a.localeCompare(b));\n"
            "      const numCellC = (v) => '<td class=\"num' + (v > 0 ? '' : ' muted-num') + '\" title=\"' + gmvFmtFull(v) + ' MAD\">' + (v > 0 ? gmvFmtCompact(v) : '0') + '</td>';\n"
            "      let catHtml = '';\n"
            "      catHtml += '<div style=\"margin-top:18px;\"><div style=\"font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:var(--text-muted); margin-bottom:8px;\">GMV by Category</div>';\n"
            "      catHtml += '<div class=\"gmv-table-wrap\"><table class=\"gmv-table\"><thead><tr>' +\n"
            "        '<th>Category</th>' +\n"
            "        '<th class=\"num\">Delivered</th>';\n"
            "      GMV_STATUSES.filter(s => s !== 'DELIVERED').forEach(s => {\n"
            "        const lbl = s === 'PENDING' ? niceStatusC(s) + ' <sup style=\"color:var(--text-soft); font-weight:600; font-size:9px;\" title=\"All-time backlog \\u2014 ignores the active period\">all</sup>' : niceStatusC(s);\n"
            "        catHtml += '<th class=\"num\" title=\"' + s + '\">' + lbl + '</th>';\n"
            "      });\n"
            "      catHtml += '</tr></thead><tbody>';\n"
            "      cats.forEach(ct => {\n"
            "        const m = byCategoryByStatus[ct] || {};\n"
            "        const delivered = m['DELIVERED'] || 0;\n"
            "        catHtml += '<tr class=\"gmv-row-seller\">' +\n"
            "          '<td><div class=\"gmv-seller-name\">' + escapeHtml(ct) + '</div></td>' +\n"
            "          '<td class=\"num\" title=\"' + gmvFmtFull(delivered) + ' MAD\">' + gmvFmtCompact(delivered) + '</td>';\n"
            "        GMV_STATUSES.filter(s => s !== 'DELIVERED').forEach(s => {\n"
            "          catHtml += numCellC(m[s] || 0);\n"
            "        });\n"
            "        catHtml += '</tr>';\n"
            "      });\n"
            "      const _totalDeliveredC = (result.totalByStatus && result.totalByStatus['DELIVERED']) || 0;\n"
            "      catHtml += '</tbody><tfoot><tr>' +\n"
            "        '<td>Grand total</td>' +\n"
            "        '<td class=\"num\" title=\"' + gmvFmtFull(_totalDeliveredC) + ' MAD\">' + gmvFmtCompact(_totalDeliveredC) + '</td>';\n"
            "      GMV_STATUSES.filter(s => s !== 'DELIVERED').forEach(s => {\n"
            "        catHtml += numCellC((result.totalByStatus && result.totalByStatus[s]) || 0);\n"
            "      });\n"
            "      catHtml += '</tr></tfoot></table></div></div>';\n"
            "      window.__gmvByCategoryFragment = catHtml;\n"
            "    } else {\n"
            "      window.__gmvByCategoryFragment = '';\n"
            "    }\n"
            "  } else {\n"
            "    window.__gmvByStoreFragment = '';\n"
            "    window.__gmvByCategoryFragment = '';\n"
            "  }"
        )
        src = must_replace_once(src, anchor_k, replacement_k, "K1: byCategory fragment build")

        # Append the fragment AFTER the byStore fragment in the wrap.innerHTML
        src = must_replace_once(
            src,
            "  if (window.__gmvByStoreFragment) html += window.__gmvByStoreFragment;",
            "  if (window.__gmvByStoreFragment) html += window.__gmvByStoreFragment;\n  if (window.__gmvByCategoryFragment) html += window.__gmvByCategoryFragment;",
            "K2: append by-cat fragment"
        )
        changed = True
        print("[OK] K: Performance by Category table now rendered")
    else:
        print("[skip] K already applied")

    # ---------- L: UI tile (3rd upload card + summary pill) ----------
    if "gmvCategoriesFile" not in src:
        # 1) Insert the new pill in the data-source strip summary (after Orders pill).
        src = must_replace_once(
            src,
            "        <span class=\"ds-pill\" id=\"gmvDsOrdersPill\">\n          <span class=\"ds-check\">○</span>\n          <span>Orders</span>\n          <span class=\"ds-count\" id=\"gmvDsOrdersCount\">not loaded</span>\n        </span>",
            "        <span class=\"ds-pill\" id=\"gmvDsOrdersPill\">\n          <span class=\"ds-check\">○</span>\n          <span>Orders</span>\n          <span class=\"ds-count\" id=\"gmvDsOrdersCount\">not loaded</span>\n        </span>\n        <span class=\"ds-pill\" id=\"gmvDsCategoriesPill\">\n          <span class=\"ds-check\">○</span>\n          <span>Categories</span>\n          <span class=\"ds-count\" id=\"gmvDsCategoriesCount\">not loaded</span>\n        </span>",
            "L1: ds pill"
        )
        # 2) Insert the new card after the Orders card.
        new_card = (
            "        <div class=\"gmv-ds-card\">\n"
            "          <div class=\"ds-card-title\">3 · Product Categories</div>\n"
            "          <label class=\"file-drop\">\n"
            "            <div class=\"file-drop-icon\">\n"
            "              <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4\"/><polyline points=\"17 8 12 3 7 8\"/><line x1=\"12\" y1=\"3\" x2=\"12\" y2=\"15\"/></svg>\n"
            "            </div>\n"
            "            <div class=\"file-drop-text\">\n"
            "              <div class=\"file-drop-title\">Drop product categories file</div>\n"
            "              <div class=\"file-drop-hint\">code · description · category (columns: Code / Description / Category)</div>\n"
            "            </div>\n"
            "            <input type=\"file\" id=\"gmvCategoriesFile\" accept=\".xlsx,.xls,.csv\">\n"
            "          </label>\n"
            "          <div id=\"gmvCategoriesSummary\" class=\"gmv-summary\" style=\"display:none;\"></div>\n"
            "        </div>\n"
            "      </div>\n"
            "    </details>"
        )
        # Anchor: the closing of the orders card + body + details.
        src = must_replace_once(
            src,
            "          <div id=\"gmvOrdersSummary\" class=\"gmv-summary\" style=\"display:none;\"></div>\n        </div>\n      </div>\n    </details>",
            "          <div id=\"gmvOrdersSummary\" class=\"gmv-summary\" style=\"display:none;\"></div>\n        </div>\n" + new_card,
            "L2: ds card"
        )
        changed = True
        print("[OK] L: UI tile + pill inserted")
    else:
        print("[skip] L already applied")

    # ---------- Done. Write back. ----------
    if not changed:
        print("\nNothing to change — file is already fully patched.")
        return
    backup = path + ".bak"
    if not os.path.exists(backup):
        with open(backup, 'w', encoding='utf-8') as f:
            # keep a one-time backup of the pre-patch file
            with open(path, 'r', encoding='utf-8') as orig:
                f.write(orig.read())
        print("[backup] saved original to: " + backup)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(src)
    delta = len(src) - original_len
    print("\nWrote patched file (" + ("+" if delta >= 0 else "") + str(delta) + " bytes).")
    print("All done. Hard-refresh the app (Ctrl+Shift+R) and you should see the 3rd upload tile in GMV Tracker.")

if __name__ == '__main__':
    if not os.path.exists(TARGET):
        sys.exit("[FAIL] target file not found:\n  " + TARGET)
    apply_patch(TARGET)
