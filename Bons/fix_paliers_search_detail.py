# -*- coding: utf-8 -*-
"""
Paliers tab — client search bar + richer product detail.

  * Search input (filters cards by name / phone / case-insensitive substring).
  * Expanded product list now shows EVERY focus product, selected or not,
    with delivered qty + delivered MAD across May+June and a progress bar
    to the SKU's minimum.
"""
import io, sys

P = '/sessions/vibrant-tender-mayer/mnt/Rehab app ( planner) - Copie/rigab_app/index.html'
src = io.open(P, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'

def go(s, old, new, label):
    o = old.replace('\n', nl); n = new.replace('\n', nl)
    if n in s and o not in s:
        print('  [skip] ' + label); return s
    if o not in s:
        print('  [FAIL] ' + label); sys.exit(2)
    if s.count(o) != 1:
        print('  [FAIL] ' + label + ' (count ' + str(s.count(o)) + ')'); sys.exit(2)
    print('  [ok]   ' + label); return s.replace(o, n, 1)


# 1) Apply the search filter to myPhones BEFORE rendering cards.
#    Anchor: the existing sort + sortedPaliers blocks added by the
#    progressive patch.
src = go(src,
    "  myPhones.sort((a, b) => {\n"
    "    const na = (((gmv.clients || {})[a] || {}).name || '').toLowerCase();\n"
    "    const nb = (((gmv.clients || {})[b] || {}).name || '').toLowerCase();\n"
    "    return na.localeCompare(nb);\n"
    "  });\n",
    "  myPhones.sort((a, b) => {\n"
    "    const na = (((gmv.clients || {})[a] || {}).name || '').toLowerCase();\n"
    "    const nb = (((gmv.clients || {})[b] || {}).name || '').toLowerCase();\n"
    "    return na.localeCompare(nb);\n"
    "  });\n"
    "  // Persistent search term across re-renders.\n"
    "  const _palQ = (gmvEngagement.paliersSearch || '').trim().toLowerCase();\n"
    "  const myPhonesAll = myPhones.slice();\n"
    "  const myPhonesFiltered = _palQ\n"
    "    ? myPhones.filter(p => {\n"
    "        const c = (gmv.clients || {})[p] || {};\n"
    "        return ((c.name || '') + ' ' + p).toLowerCase().includes(_palQ);\n"
    "      })\n"
    "    : myPhones;\n",
    'add filter step using gmvEngagement.paliersSearch')


# 2) Replace expanded product list with the richer detail block.
src = go(src,
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
    "          </div>\n",
    "          <div data-pal-products=\"${gmvEscapeHtmlEng(phone)}\" style=\"display:none; margin-top:10px; max-height:320px; overflow-y:auto; padding:8px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px;\">\n"
    "            ${(() => {\n"
    "              if (!focusCodes.length) return `<div style=\"color:#94a3b8; font-size:12px; padding:6px;\">${engT('eng_no_focus')}</div>`;\n"
    "              // Pre-compute per-product delivered qty & GMV across both campaign months.\n"
    "              const sM1 = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M1);\n"
    "              const sM2 = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M2);\n"
    "              // Sort: selected first, then by delivered qty desc, then by code.\n"
    "              const sorted = focusCodes.slice().sort((a, b) => {\n"
    "                const sa = !!(cFocus[phone] && cFocus[phone][a] && cFocus[phone][a].selected);\n"
    "                const sb = !!(cFocus[phone] && cFocus[phone][b] && cFocus[phone][b].selected);\n"
    "                if (sa !== sb) return sa ? -1 : 1;\n"
    "                const qa = ((sM1[a] && sM1[a].qty) || 0) + ((sM2[a] && sM2[a].qty) || 0);\n"
    "                const qb = ((sM1[b] && sM1[b].qty) || 0) + ((sM2[b] && sM2[b].qty) || 0);\n"
    "                if (qa !== qb) return qb - qa;\n"
    "                return a.localeCompare(b);\n"
    "              });\n"
    "              return sorted.map(code => {\n"
    "                const meta = gmvEngagement.focusProducts[code] || {};\n"
    "                const checked = !!(cFocus[phone] && cFocus[phone][code] && cFocus[phone][code].selected);\n"
    "                const qty = ((sM1[code] && sM1[code].qty) || 0) + ((sM2[code] && sM2[code].qty) || 0);\n"
    "                const mad = ((sM1[code] && sM1[code].gmv) || 0) + ((sM2[code] && sM2[code].gmv) || 0);\n"
    "                const min = meta.min || 0;\n"
    "                const hit = min > 0 && qty >= min;\n"
    "                const pct = min > 0 ? Math.min(100, Math.round((qty / min) * 100)) : (qty > 0 ? 100 : 0);\n"
    "                const nm = (meta.name || '').slice(0, 36);\n"
    "                const rowBg = hit ? '#f0fdf4' : (checked ? '#fff' : 'transparent');\n"
    "                const borderC = hit ? '#86efac' : (checked ? '#cbd5e1' : 'transparent');\n"
    "                return `<label style=\"display:flex; align-items:flex-start; gap:8px; padding:8px; margin-bottom:6px; font-size:12px; cursor:pointer; border-radius:6px; background:${rowBg}; border:1px solid ${borderC};\">\n"
    "                  <input type=\"checkbox\" data-pal-prod=\"${gmvEscapeHtmlEng(phone)}\" value=\"${gmvEscapeHtmlEng(code)}\" ${checked ? 'checked' : ''} style=\"cursor:pointer; flex-shrink:0; margin-top:1px;\">\n"
    "                  <div style=\"flex:1; min-width:0;\">\n"
    "                    <div style=\"display:flex; gap:6px; align-items:baseline;\">\n"
    "                      <b style=\"color:#0f172a; flex-shrink:0;\">${gmvEscapeHtmlEng(code)}</b>\n"
    "                      ${nm ? `<span style=\"color:#475569; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1; min-width:0;\">${gmvEscapeHtmlEng(nm)}</span>` : ''}\n"
    "                      ${hit ? '<span style=\"color:#16a34a; font-weight:700; flex-shrink:0;\">✓</span>' : ''}\n"
    "                    </div>\n"
    "                    <div style=\"display:flex; gap:10px; flex-wrap:wrap; font-size:11px; color:#64748b; margin-top:3px;\">\n"
    "                      <span>${engT('pal_delivered')}: <b style=\"color:${hit ? '#16a34a' : '#0f172a'};\">${qty}</b>${min > 0 ? ' / ' + min : ''} ${engT('pal_units')}</span>\n"
    "                      <span>${fmt(mad)} MAD</span>\n"
    "                    </div>\n"
    "                    ${min > 0 ? `<div style=\"height:3px; background:#e2e8f0; border-radius:99px; overflow:hidden; margin-top:5px;\">\n"
    "                      <div style=\"height:100%; width:${pct}%; background:${hit ? '#16a34a' : '#3b82f6'}; transition:width .4s;\"></div>\n"
    "                    </div>` : ''}\n"
    "                  </div>\n"
    "                </label>`;\n"
    "              }).join('');\n"
    "            })()}\n"
    "          </div>\n",
    'expanded list shows delivered qty + MAD per product')


# 3) Replace the cards header to include the search input + filtered count.
src = go(src,
    "  panel.innerHTML = `\n"
    "    <div style=\"display:flex; gap:8px; align-items:center; margin:0 0 12px;\">\n"
    "      <span style=\"font-size:13px;\">${myPhones.length} ${engT('pal_clients')}</span>\n"
    "      <button type=\"button\" id=\"engSavePaliers\" class=\"btn btn-primary\" style=\"margin-left:auto; font-size:12px; padding:8px 14px; background:#0f172a; color:#fff; border:0; border-radius:8px; font-weight:600; cursor:pointer;\">${engT('eng_save')}</button>\n"
    "    </div>\n"
    "    ${cardsHtml}`;\n",
    "  const _filtCount = myPhonesFiltered.length;\n"
    "  const _totCount  = myPhonesAll.length;\n"
    "  const _countTxt  = (_palQ && _filtCount !== _totCount)\n"
    "    ? (_filtCount + ' / ' + _totCount + ' ' + engT('pal_clients'))\n"
    "    : (_totCount + ' ' + engT('pal_clients'));\n"
    "  panel.innerHTML = `\n"
    "    <div style=\"display:flex; gap:8px; align-items:center; margin:0 0 10px; flex-wrap:wrap;\">\n"
    "      <input type=\"search\" id=\"palSearch\" placeholder=\"${engT('pal_search')}\" value=\"${gmvEscapeHtmlEng(_palQ)}\" autocomplete=\"off\" style=\"flex:1; min-width:160px; padding:8px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:13px; background:#fff;\" />\n"
    "      <button type=\"button\" id=\"engSavePaliers\" class=\"btn btn-primary\" style=\"font-size:12px; padding:8px 14px; background:#0f172a; color:#fff; border:0; border-radius:8px; font-weight:600; cursor:pointer; flex-shrink:0;\">${engT('eng_save')}</button>\n"
    "    </div>\n"
    "    <div style=\"font-size:12px; color:#64748b; margin:0 0 10px;\">${_countTxt}</div>\n"
    "    ${cardsHtml}`;\n",
    'add search input + filtered count to header')


# 4) Replace the cards-loop driver from myPhones.forEach to myPhonesFiltered.forEach.
src = go(src,
    "  let cardsHtml = '';\n"
    "  myPhones.forEach(phone => {\n",
    "  let cardsHtml = '';\n"
    "  myPhonesFiltered.forEach(phone => {\n",
    'iterate filtered phones for cards rendering')


# Empty-state when search yields zero results.
src = go(src,
    "  myPhonesFiltered.forEach(phone => {\n",
    "  if (!myPhonesFiltered.length) {\n"
    "    cardsHtml = `<div style=\"padding:32px 16px; text-align:center; color:#94a3b8; font-size:13px; background:#f8fafc; border:1px dashed #cbd5e1; border-radius:12px;\">${engT('pal_no_match')}</div>`;\n"
    "  }\n"
    "  myPhonesFiltered.forEach(phone => {\n",
    'empty-state when search has no match')


# 5) Wire the search input AFTER setting innerHTML.
src = go(src,
    "  // Wire expand toggles for the per-client product list.\n",
    "  // Wire the search input — debounced to keep typing snappy.\n"
    "  const _palSearch = document.getElementById('palSearch');\n"
    "  if (_palSearch) {\n"
    "    let _palDebounce = null;\n"
    "    _palSearch.addEventListener('input', () => {\n"
    "      clearTimeout(_palDebounce);\n"
    "      _palDebounce = setTimeout(() => {\n"
    "        gmvEngagement.paliersSearch = _palSearch.value || '';\n"
    "        gmvRenderEngagementPaliers(panel, mySeller, isCreator);\n"
    "        // Restore focus + caret position so typing isn't interrupted.\n"
    "        const after = document.getElementById('palSearch');\n"
    "        if (after) { after.focus(); try { after.setSelectionRange(after.value.length, after.value.length); } catch (_) {} }\n"
    "      }, 120);\n"
    "    });\n"
    "  }\n"
    "  // Wire expand toggles for the per-client product list.\n",
    'wire #palSearch input handler')


# 6) Add the new i18n keys (FR / EN / AR).
src = go(src,
    "    pal_my_products: 'Mes produits engagés',\n",
    "    pal_my_products: 'Mes produits engagés',\n"
    "    pal_search: 'Rechercher un client...', pal_no_match: 'Aucun client ne correspond à la recherche.',\n"
    "    pal_delivered: 'Livré', pal_units: 'unités',\n",
    'i18n FR: pal_search / pal_delivered / pal_units / pal_no_match')

src = go(src,
    "    pal_my_products: 'My committed products',\n",
    "    pal_my_products: 'My committed products',\n"
    "    pal_search: 'Search clients...', pal_no_match: 'No clients match the search.',\n"
    "    pal_delivered: 'Delivered', pal_units: 'units',\n",
    'i18n EN: pal_search / pal_delivered / pal_units / pal_no_match')

src = go(src,
    "    pal_my_products: 'منتجاتي الملتزم بها',\n",
    "    pal_my_products: 'منتجاتي الملتزم بها',\n"
    "    pal_search: 'البحث عن زبون...', pal_no_match: 'لا يوجد زبون يطابق البحث.',\n"
    "    pal_delivered: 'تم تسليمه', pal_units: 'وحدة',\n",
    'i18n AR: pal_search / pal_delivered / pal_units / pal_no_match')


io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
