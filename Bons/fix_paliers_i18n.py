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
    "    pal_next_target: 'Prochain palier', pal_remaining: '{n} MAD restants pour le débloquer',\n"
    "    pal_all_done: '🎉 Tous les paliers atteints !',\n",
    'FR keys')

src = go(src,
    "    pal_target: 'Target palier', pal_my_products: 'My committed products',\n",
    "    pal_target: 'Target palier', pal_my_products: 'My committed products',\n"
    "    pal_next_target: 'Next palier', pal_remaining: '{n} MAD to go to unlock it',\n"
    "    pal_all_done: '🎉 All paliers achieved!',\n",
    'EN keys')

src = go(src,
    "    pal_target: 'المستوى المستهدف', pal_my_products: 'منتجاتي الملتزم بها',\n",
    "    pal_target: 'المستوى المستهدف', pal_my_products: 'منتجاتي الملتزم بها',\n"
    "    pal_next_target: 'المستوى التالي', pal_remaining: 'متبقي {n} درهم لفتحه',\n"
    "    pal_all_done: '🎉 تم بلوغ كل المستويات !',\n",
    'AR keys')

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
