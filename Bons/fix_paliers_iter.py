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

# Replace myPhones.forEach with myPhonesFiltered.forEach + add empty-state guard
src = go(src,
    "  // Sort paliers ascending so the auto-progression has stable ordering.\n"
    "  const sortedPaliers = (gmvEngagement.paliers || []).slice().sort((a, b) => (a.palier || 0) - (b.palier || 0));\n"
    "  myPhones.forEach(phone => {\n",
    "  // Sort paliers ascending so the auto-progression has stable ordering.\n"
    "  const sortedPaliers = (gmvEngagement.paliers || []).slice().sort((a, b) => (a.palier || 0) - (b.palier || 0));\n"
    "  if (!myPhonesFiltered.length) {\n"
    "    cardsHtml = `<div style=\"padding:32px 16px; text-align:center; color:#94a3b8; font-size:13px; background:#f8fafc; border:1px dashed #cbd5e1; border-radius:12px;\">${engT('pal_no_match')}</div>`;\n"
    "  }\n"
    "  myPhonesFiltered.forEach(phone => {\n",
    'iterate filtered phones + empty-state')

# Also wire the search input
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
    "        const after = document.getElementById('palSearch');\n"
    "        if (after) { after.focus(); try { after.setSelectionRange(after.value.length, after.value.length); } catch (_) {} }\n"
    "      }, 120);\n"
    "    });\n"
    "  }\n"
    "  // Wire expand toggles for the per-client product list.\n",
    'wire #palSearch input handler')

# i18n
src = go(src,
    "    pal_my_products: 'Mes produits engagés',\n",
    "    pal_my_products: 'Mes produits engagés',\n"
    "    pal_search: 'Rechercher un client...', pal_no_match: 'Aucun client ne correspond à la recherche.',\n"
    "    pal_delivered: 'Livré', pal_units: 'unités',\n",
    'FR i18n')

src = go(src,
    "    pal_my_products: 'My committed products',\n",
    "    pal_my_products: 'My committed products',\n"
    "    pal_search: 'Search clients...', pal_no_match: 'No clients match the search.',\n"
    "    pal_delivered: 'Delivered', pal_units: 'units',\n",
    'EN i18n')

src = go(src,
    "    pal_my_products: 'منتجاتي الملتزم بها',\n",
    "    pal_my_products: 'منتجاتي الملتزم بها',\n"
    "    pal_search: 'البحث عن زبون...', pal_no_match: 'لا يوجد زبون يطابق البحث.',\n"
    "    pal_delivered: 'تم تسليمه', pal_units: 'وحدة',\n",
    'AR i18n')

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
