# -*- coding: utf-8 -*-
"""
Make per-client product selection the obvious primary task on the
Paliers de mes clients page.

  1. Setup banner: appears at the top whenever ≥1 of the seller's clients
     has 0 committed products. States the count and links them to the
     idle section + auto-opens it. Disappears once every client has a
     commitment list.
  2. Amber accent + "Setup needed" badge on cards where myProds.length === 0
     (NOT just under-minimum — strictly zero).
  3. Cards with zero commits are sorted first within the idle section.
  4. The collapsed-summary "0/10 products" chip turns to a "Choose products"
     button with a clear CTA color when commits === 0.
"""
import io, sys

P = '/sessions/vibrant-tender-mayer/mnt/Rehab app ( planner) - Copie/rigab_app/index.html'
src = io.open(P, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'

def go(s, old, new, label):
    o = old.replace('\n', nl); n = new.replace('\n', nl)
    if n in s and o not in s: print('  [skip] ' + label); return s
    if o not in s: print('  [FAIL] ' + label); sys.exit(2)
    if s.count(o) != 1: print('  [FAIL] ' + label + ' (count ' + str(s.count(o)) + ')'); sys.exit(2)
    print('  [ok]   ' + label); return s.replace(o, n, 1)

def strip_block(s, begin, end):
    if begin not in s or end not in s: return s
    a = s.index(begin); b = s.index(end) + len(end)
    e = b
    while e < len(s) and s[e] in ('\n', '\r'): e += 1
    st = a
    while st > 0 and s[st-1] in ('\n', '\r'): st -= 1
    return s[:st] + s[e:]


# ---- 1) CSS: setup banner, needs-setup card, big CTA -----------------
CSS_BEGIN = '/* === PRODUCT SETUP SURFACE — highlight_product_selection.py === */'
CSS_END   = '/* === END PRODUCT SETUP SURFACE === */'
src = strip_block(src, CSS_BEGIN, CSS_END)

CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  /* Top-of-page setup nudge. */\n'
    '  .pal-setup-banner {\n'
    '    position: relative; overflow: hidden;\n'
    '    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);\n'
    '    border: 1px solid #fde68a;\n'
    '    border-radius: 14px;\n'
    '    padding: 14px 18px;\n'
    '    margin: 0 0 14px;\n'
    '    display: flex; align-items: center; gap: 14px; flex-wrap: wrap;\n'
    '  }\n'
    '  .pal-setup-banner-icon {\n'
    '    width: 44px; height: 44px; border-radius: 50%;\n'
    '    background: #fef3c7; color: #b45309;\n'
    '    display: inline-flex; align-items: center; justify-content: center;\n'
    '    font-size: 22px; flex-shrink: 0;\n'
    '    box-shadow: inset 0 0 0 1px #fcd34d;\n'
    '  }\n'
    '  .pal-setup-banner-text { flex: 1; min-width: 0; }\n'
    '  .pal-setup-banner-title {\n'
    '    font-size: 14px; font-weight: 800; color: #78350f;\n'
    '    line-height: 1.3;\n'
    '  }\n'
    '  .pal-setup-banner-sub {\n'
    '    font-size: 12px; color: #92400e; margin-top: 3px; line-height: 1.4;\n'
    '  }\n'
    '  .pal-setup-banner-btn {\n'
    '    background: #b45309; color: #fff; border: 0;\n'
    '    padding: 9px 16px; border-radius: 10px;\n'
    '    font-size: 12px; font-weight: 700; cursor: pointer;\n'
    '    flex-shrink: 0; transition: background .12s, transform .08s;\n'
    '  }\n'
    '  .pal-setup-banner-btn:hover  { background: #92400e; }\n'
    '  .pal-setup-banner-btn:active { transform: scale(.97); }\n'
    '\n'
    '  /* Needs-setup state on the per-client card. */\n'
    '  .pcard.pcard--needs-setup {\n'
    '    border-color: #fcd34d;\n'
    '    background: linear-gradient(180deg, #fffbeb 0%, #fff 50%);\n'
    '    box-shadow: 0 1px 2px rgba(180, 83, 9, .08);\n'
    '  }\n'
    '  .pcard-needs-badge {\n'
    '    display: inline-flex; align-items: center; gap: 4px;\n'
    '    padding: 3px 9px; border-radius: 99px;\n'
    '    background: #fef3c7; color: #b45309;\n'
    '    font-size: 10.5px; font-weight: 800;\n'
    '    text-transform: uppercase; letter-spacing: .06em;\n'
    '    border: 1px solid #fcd34d;\n'
    '    line-height: 1.4;\n'
    '  }\n'
    '\n'
    '  /* Big CTA inside an unset card. */\n'
    '  .pcard-setup-cta {\n'
    '    display: flex; align-items: center; gap: 10px;\n'
    '    padding: 12px 14px;\n'
    '    background: #fff;\n'
    '    border: 1.5px dashed #fcd34d;\n'
    '    border-radius: 10px;\n'
    '    margin-top: 10px;\n'
    '    width: 100%;\n'
    '    cursor: pointer; user-select: none;\n'
    '    color: #78350f;\n'
    '    transition: background .12s, border-color .12s;\n'
    '  }\n'
    '  .pcard-setup-cta:hover { background: #fffbeb; border-color: #f59e0b; }\n'
    '  .pcard-setup-cta-icon {\n'
    '    width: 28px; height: 28px; border-radius: 50%;\n'
    '    background: #fef3c7; color: #b45309;\n'
    '    display: inline-flex; align-items: center; justify-content: center;\n'
    '    font-size: 14px; flex-shrink: 0; font-weight: 800;\n'
    '  }\n'
    '  .pcard-setup-cta-text { flex: 1; min-width: 0; }\n'
    '  .pcard-setup-cta-title {\n'
    '    font-size: 12.5px; font-weight: 800; color: #78350f; line-height: 1.2;\n'
    '  }\n'
    '  .pcard-setup-cta-sub {\n'
    '    font-size: 11px; color: #92400e; margin-top: 2px;\n'
    '  }\n'
    '  .pcard-setup-cta-arrow {\n'
    '    color: #b45309; font-size: 16px; flex-shrink: 0;\n'
    '  }\n'
    + CSS_END
)

css_anchor = '/* === END PALIERS POLISH === */'
if css_anchor not in src:
    print('  [FAIL] CSS anchor not found'); sys.exit(2)
src = src.replace(css_anchor, css_anchor + nl + '  ' + CSS_BLOCK.replace('\n', nl), 1)
print('  [ok]   injected setup-surface CSS')


# ---- 2) Compute "needs setup" + reorder idle bucket ------------------
# After classifying the bucket, also tag needsSetup = myProds.length === 0.
src = go(src,
    "    // Classify into a bucket BEFORE building the HTML, so we can route it.\n"
    "    const _bucketKey = (m1Open || bothOpen)\n"
    "      ? 'won'\n"
    "      : (prodOk ? 'ok' : 'idle');\n"
    "    _counts[_bucketKey]++;\n",
    "    // Classify into a bucket BEFORE building the HTML, so we can route it.\n"
    "    const _bucketKey = (m1Open || bothOpen)\n"
    "      ? 'won'\n"
    "      : (prodOk ? 'ok' : 'idle');\n"
    "    _counts[_bucketKey]++;\n"
    "    const _needsSetup = myProds.length === 0;\n"
    "    if (_needsSetup) _counts.needs = (_counts.needs || 0) + 1;\n",
    'compute needsSetup flag + count')


# ---- 3) Sort idle bucket so needs-setup clients appear first ---------
# After the forEach loop, reorder _bucket.idle by prepending any cards
# carrying the "needs-setup" marker. We'll do this with a regex split
# on the marker we'll emit on those cards.
# Easiest: do this by maintaining two arrays during the loop. We add a
# secondary bucket idleHead for needs-setup, then concatenate.
src = go(src,
    "  // Three buckets: clients with an unlocked gift, those at minimum\n"
    "  // products, and those who haven't engaged yet.\n"
    "  const _bucket = { won: '', ok: '', idle: '' };\n"
    "  const _counts = { won: 0, ok: 0, idle: 0 };\n",
    "  // Three buckets: clients with an unlocked gift, those at minimum\n"
    "  // products, and those who haven't engaged yet. idleHead collects\n"
    "  // the zero-commit cards so they surface first in their section.\n"
    "  const _bucket = { won: '', ok: '', idle: '', idleHead: '' };\n"
    "  const _counts = { won: 0, ok: 0, idle: 0, needs: 0 };\n",
    'declare idleHead + needs count')

# Routing: when _needsSetup is true and bucket is idle, append to idleHead.
src = go(src,
    "    _bucket[_bucketKey] += `\n"
    "      <article class=\"pcard${_open ? ' pcard--open' : ''}\">\n",
    "    const _routeKey = (_needsSetup && _bucketKey === 'idle') ? 'idleHead' : _bucketKey;\n"
    "    _bucket[_routeKey] += `\n"
    "      <article class=\"pcard${_open ? ' pcard--open' : ''}${_needsSetup ? ' pcard--needs-setup' : ''}\">\n",
    'route needs-setup cards to idleHead + add class')


# ---- 4) Show the "Setup needed" badge in the header right-side -------
src = go(src,
    "          <div class=\"pcard-head-right\">\n"
    "            ${ach ? `<span class=\"pcard-badge\">${engT('pal_achieved')} ${ach.palier}</span>` : ''}\n"
    "            <span class=\"pcard-chevron\" aria-hidden=\"true\">▾</span>\n"
    "          </div>\n",
    "          <div class=\"pcard-head-right\">\n"
    "            ${_needsSetup ? `<span class=\"pcard-needs-badge\">⚙ ${engT('pal_setup_needed')}</span>` : (ach ? `<span class=\"pcard-badge\">${engT('pal_achieved')} ${ach.palier}</span>` : '')}\n"
    "            <span class=\"pcard-chevron\" aria-hidden=\"true\">▾</span>\n"
    "          </div>\n",
    'header right: needs-setup badge takes priority')


# ---- 5) Replace the products row in pcard-commit with a CTA when zero --
src = go(src,
    "        <section class=\"pcard-commit\">\n"
    "          <div class=\"pcard-commit-row\">\n"
    "            <div class=\"pcard-commit-label\">${engT('pal_my_products')}</div>\n"
    "            <div class=\"pcard-commit-count ${prodOk ? 'is-ok' : 'is-low'}\">${myProds.length}<span class=\"denom\"> / ${ENG_CLIENT_MIN_PRODUCTS}</span></div>\n"
    "            <button type=\"button\" data-pal-edit=\"${gmvEscapeHtmlEng(phone)}\" class=\"pcard-commit-btn\">${engT('pal_edit')}</button>\n"
    "          </div>\n"
    "          <div class=\"pcard-commit-bar${prodOk ? ' is-ok' : ''}\"><span style=\"width:${prodPct}%\"></span></div>\n",
    "        <section class=\"pcard-commit\">\n"
    "          <div class=\"pcard-commit-row\">\n"
    "            <div class=\"pcard-commit-label\">${engT('pal_my_products')}</div>\n"
    "            <div class=\"pcard-commit-count ${prodOk ? 'is-ok' : 'is-low'}\">${myProds.length}<span class=\"denom\"> / ${ENG_CLIENT_MIN_PRODUCTS}</span></div>\n"
    "            <button type=\"button\" data-pal-edit=\"${gmvEscapeHtmlEng(phone)}\" class=\"pcard-commit-btn\">${myProds.length === 0 ? engT('pal_choose_products') : engT('pal_edit')}</button>\n"
    "          </div>\n"
    "          ${_needsSetup ? `<button type=\"button\" data-pal-edit=\"${gmvEscapeHtmlEng(phone)}\" class=\"pcard-setup-cta\">\n"
    "            <span class=\"pcard-setup-cta-icon\">+</span>\n"
    "            <span class=\"pcard-setup-cta-text\">\n"
    "              <span class=\"pcard-setup-cta-title\">${engT('pal_setup_cta_t')}</span>\n"
    "              <span class=\"pcard-setup-cta-sub\">${engT('pal_setup_cta_d')}</span>\n"
    "            </span>\n"
    "            <span class=\"pcard-setup-cta-arrow\">→</span>\n"
    "          </button>` : `<div class=\"pcard-commit-bar${prodOk ? ' is-ok' : ''}\"><span style=\"width:${prodPct}%\"></span></div>`}\n",
    'commit row: dashed CTA + better button label when zero')


# ---- 6) Render the setup banner at the top of the page ---------------
# Insert just after the portfolio hero, before the search row.
src = go(src,
    "  panel.innerHTML = `\n"
    "    ${_portfolioHero}\n"
    "    <div style=\"display:flex; gap:10px; align-items:center; margin:0 0 12px; flex-wrap:wrap;\">\n",
    "  // Setup banner (only shown when at least one client has no products).\n"
    "  const _needsCount = myPhonesAll.reduce((c, p) => {\n"
    "    const arr = Object.keys(cFocus[p] || {}).filter(k => cFocus[p][k] && cFocus[p][k].selected);\n"
    "    return arr.length === 0 ? c + 1 : c;\n"
    "  }, 0);\n"
    "  const _setupBanner = _needsCount > 0 ? `\n"
    "    <section class=\"pal-setup-banner\">\n"
    "      <div class=\"pal-setup-banner-icon\">⚙</div>\n"
    "      <div class=\"pal-setup-banner-text\">\n"
    "        <div class=\"pal-setup-banner-title\">${engT('pal_setup_banner_t', { n: _needsCount })}</div>\n"
    "        <div class=\"pal-setup-banner-sub\">${engT('pal_setup_banner_d')}</div>\n"
    "      </div>\n"
    "      <button type=\"button\" id=\"palSetupJump\" class=\"pal-setup-banner-btn\">${engT('pal_setup_banner_cta')}</button>\n"
    "    </section>` : '';\n"
    "  panel.innerHTML = `\n"
    "    ${_portfolioHero}\n"
    "    ${_setupBanner}\n"
    "    <div style=\"display:flex; gap:10px; align-items:center; margin:0 0 12px; flex-wrap:wrap;\">\n",
    'render setup banner above search row')


# ---- 7) Concatenate idleHead before idle in the rendered section ------
src = go(src,
    "        ${cnt > 0 ? `<div class=\"pal-cards-grid\">${_bucket[key]}</div>` : `<div class=\"pal-section-empty\">${_emptyHtml}</div>`}\n",
    "        ${cnt > 0 ? `<div class=\"pal-cards-grid\">${key === 'idle' ? (_bucket.idleHead || '') + _bucket.idle : _bucket[key]}</div>` : `<div class=\"pal-section-empty\">${_emptyHtml}</div>`}\n",
    'render: prepend idleHead in the idle section')


# ---- 8) Wire the banner button: jump to + open idle section ----------
src = go(src,
    "  // Wire section-head toggles (open/close a whole status group).\n",
    "  // Wire the setup banner: open the idle section and scroll to it.\n"
    "  const _setupJump = document.getElementById('palSetupJump');\n"
    "  if (_setupJump) _setupJump.addEventListener('click', () => {\n"
    "    if (!gmvEngagement.expandedSections) gmvEngagement.expandedSections = {};\n"
    "    gmvEngagement.expandedSections.idle = true;\n"
    "    const sec = panel.querySelector('[data-pal-section=\"idle\"]');\n"
    "    if (sec) {\n"
    "      sec.closest('.pal-section').classList.add('pal-section--open');\n"
    "      sec.scrollIntoView({ behavior: 'smooth', block: 'start' });\n"
    "    }\n"
    "  });\n"
    "  // Wire section-head toggles (open/close a whole status group).\n",
    'wire setup-banner jump button')


# ---- 9) i18n keys (FR / EN / AR) -------------------------------------
def add_after(s, anchor, addition, label):
    o = anchor.replace('\n', nl)
    n = o + addition.replace('\n', nl)
    if n in s and o not in s: print('  [skip] ' + label); return s
    if o not in s: print('  [FAIL] ' + label); sys.exit(2)
    if s.count(o) != 1: print('  [FAIL] ' + label + ' (count ' + str(s.count(o)) + ')'); sys.exit(2)
    print('  [ok]   ' + label)
    return s.replace(o, n, 1)

src = add_after(src,
    "    pal_portfolio: 'Mon portefeuille', pal_prize_at: 'au',\n",
    "    pal_setup_needed: 'À configurer', pal_choose_products: 'Choisir mes produits',\n"
    "    pal_setup_cta_t: 'Choisir mes produits pour ce client', pal_setup_cta_d: 'Sélectionner ≥10 produits avec leurs montants minimum.',\n"
    "    pal_setup_banner_t: '{n} client(s) sans produits engagés', pal_setup_banner_d: 'Pour chaque zbon, sélectionnez ≥10 produits parmi la liste focus.', pal_setup_banner_cta: 'Configurer maintenant →',\n",
    'FR setup-banner i18n')

src = add_after(src,
    "    pal_portfolio: 'My portfolio', pal_prize_at: 'at',\n",
    "    pal_setup_needed: 'Setup', pal_choose_products: 'Choose products',\n"
    "    pal_setup_cta_t: 'Choose products for this client', pal_setup_cta_d: 'Pick ≥10 focus SKUs with their MAD minimums.',\n"
    "    pal_setup_banner_t: '{n} client(s) without committed products', pal_setup_banner_d: 'For each client, pick ≥10 products from the focus list.', pal_setup_banner_cta: 'Set up now →',\n",
    'EN setup-banner i18n')

src = add_after(src,
    "    pal_portfolio: 'محفظتي', pal_prize_at: 'في',\n",
    "    pal_setup_needed: 'يحتاج إعداد', pal_choose_products: 'اختر منتجاتي',\n"
    "    pal_setup_cta_t: 'اختر منتجاتك لهذا الزبون', pal_setup_cta_d: 'اختر 10 منتجات على الأقل من قائمة المنتجات المختارة.',\n"
    "    pal_setup_banner_t: '{n} زبون بدون منتجات ملتزم بها', pal_setup_banner_d: 'لكل زبون، اختر 10 منتجات على الأقل من القائمة.', pal_setup_banner_cta: 'بدء الإعداد ←',\n",
    'AR setup-banner i18n')


io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
