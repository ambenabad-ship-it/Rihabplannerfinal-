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

src = go(src,
    "    pal_target: 'Palier ciblé', pal_my_products: 'Mes produits engagés',\n",
    "    pal_target: 'Palier ciblé', pal_my_products: 'Mes produits engagés',\n"
    "    pal_search: 'Rechercher un client...', pal_no_match: 'Aucun client ne correspond à la recherche.',\n"
    "    pal_delivered: 'Livré', pal_units: 'unités',\n",
    'FR i18n')

src = go(src,
    "    pal_target: 'Target palier', pal_my_products: 'My committed products',\n",
    "    pal_target: 'Target palier', pal_my_products: 'My committed products',\n"
    "    pal_search: 'Search clients...', pal_no_match: 'No clients match the search.',\n"
    "    pal_delivered: 'Delivered', pal_units: 'units',\n",
    'EN i18n')

src = go(src,
    "    pal_target: 'المستوى المستهدف', pal_my_products: 'منتجاتي الملتزم بها',\n",
    "    pal_target: 'المستوى المستهدف', pal_my_products: 'منتجاتي الملتزم بها',\n"
    "    pal_search: 'البحث عن زبون...', pal_no_match: 'لا يوجد زبون يطابق البحث.',\n"
    "    pal_delivered: 'تم تسليمه', pal_units: 'وحدة',\n",
    'AR i18n')

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
