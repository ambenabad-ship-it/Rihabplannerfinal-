# -*- coding: utf-8 -*-
"""
Make the May+June 2026 campaign window unmistakably visible everywhere
on the paliers page.

  1. Portfolio hero gets a dedicated "Campagne · Mai → Juin 2026" chip.
  2. The setup banner mentions both months in its description.
  3. Per-card setup CTA states "valid for May + June 2026".
  4. Inside the expanded products list, a header line labels the months
     so the seller knows what window the delivered figures cover.
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

# ---- 1) CSS for the campaign-window chip + product list month header --
CSS_BEGIN = '/* === CAMPAIGN MONTHS LABEL — label_campaign_months.py === */'
CSS_END   = '/* === END CAMPAIGN MONTHS LABEL === */'
src = strip_block(src, CSS_BEGIN, CSS_END)

CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  /* Campaign window pill in the portfolio hero. */\n'
    '  .sb-hero-window {\n'
    '    display: inline-flex; align-items: center; gap: 6px;\n'
    '    margin-top: 10px;\n'
    '    padding: 4px 10px 4px 6px;\n'
    '    background: rgba(255, 255, 255, 0.18);\n'
    '    border: 1px solid rgba(255, 255, 255, 0.3);\n'
    '    border-radius: 99px;\n'
    '    font-size: 11px; font-weight: 700;\n'
    '    letter-spacing: .02em;\n'
    '    position: relative;\n'
    '  }\n'
    '  .sb-hero-window svg { width: 13px; height: 13px; flex-shrink: 0; }\n'
    '  .sb-hero-window b { font-weight: 800; }\n'
    '\n'
    '  /* Month coverage banner inside the expanded products picker. */\n'
    '  .pcard-prod-window {\n'
    '    display: flex; align-items: center; gap: 8px;\n'
    '    padding: 8px 10px;\n'
    '    background: linear-gradient(135deg, var(--rf-orange-soft, #fff5f3) 0%, #fff 100%);\n'
    '    border: 1px solid #fed7aa;\n'
    '    border-radius: 8px;\n'
    '    margin-bottom: 10px;\n'
    '    font-size: 11.5px; color: #9a3412;\n'
    '    font-weight: 600;\n'
    '  }\n'
    '  .pcard-prod-window svg { width: 14px; height: 14px; flex-shrink: 0; color: var(--rf-orange-dark, #d54b33); }\n'
    + CSS_END
)

css_anchor = '/* === END PRODUCT SETUP SURFACE === */'
if css_anchor not in src:
    print('  [FAIL] CSS anchor not found'); sys.exit(2)
src = src.replace(css_anchor, css_anchor + nl + '  ' + CSS_BLOCK.replace('\n', nl), 1)
print('  [ok]   injected campaign-months CSS')


# ---- 2) Add the campaign-window chip inside the portfolio hero --------
src = go(src,
    "      <div class=\"sb-hero-stats\">\n"
    "        <div class=\"sb-hero-stat\"><b>${myPhonesAll.length}</b><span>${engT('sb_stat_clients')}</span></div>\n"
    "        <div class=\"sb-hero-stat\"><b>${_giftsOpen}</b><span>${engT('sb_stat_gifts')}</span></div>\n"
    "        <div class=\"sb-hero-stat\"><b>${fmt(_gmvTotal)}</b><span>MAD · ${engT('sb_stat_gmv')}</span></div>\n"
    "      </div>\n"
    "    </section>`;\n",
    "      <div class=\"sb-hero-stats\">\n"
    "        <div class=\"sb-hero-stat\"><b>${myPhonesAll.length}</b><span>${engT('sb_stat_clients')}</span></div>\n"
    "        <div class=\"sb-hero-stat\"><b>${_giftsOpen}</b><span>${engT('sb_stat_gifts')}</span></div>\n"
    "        <div class=\"sb-hero-stat\"><b>${fmt(_gmvTotal)}</b><span>MAD · ${engT('sb_stat_gmv')}</span></div>\n"
    "      </div>\n"
    "      <div class=\"sb-hero-window\">\n"
    "        <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"5\" width=\"18\" height=\"16\" rx=\"2\"/><path d=\"M3 10h18M8 3v4M16 3v4\"/></svg>\n"
    "        ${engT('pal_campaign_window')} · <b>${engT('pal_month_may')} → ${engT('pal_month_june')}</b>\n"
    "      </div>\n"
    "    </section>`;\n",
    'portfolio hero: campaign-window chip')


# ---- 3) Setup banner copy mentions both months ------------------------
src = go(src,
    "        <div class=\"pal-setup-banner-sub\">${engT('pal_setup_banner_d')}</div>\n",
    "        <div class=\"pal-setup-banner-sub\">${engT('pal_setup_banner_d')} <b>${engT('pal_month_may')} + ${engT('pal_month_june')}</b>.</div>\n",
    'setup banner: mention may + june')


# ---- 4) Per-card setup CTA mentions both months -----------------------
src = go(src,
    "              <span class=\"pcard-setup-cta-sub\">${engT('pal_setup_cta_d')}</span>\n",
    "              <span class=\"pcard-setup-cta-sub\">${engT('pal_setup_cta_d')} <b>${engT('pal_month_may')} + ${engT('pal_month_june')}</b>.</span>\n",
    'setup CTA sub: mention may + june')


# ---- 5) Month banner inside the expanded products picker --------------
src = go(src,
    "              if (!focusCodes.length) return `<div style=\"color:#94a3b8; font-size:12px; padding:6px;\">${engT('eng_no_focus')}</div>`;\n"
    "              const sM1 = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M1);\n",
    "              if (!focusCodes.length) return `<div style=\"color:#94a3b8; font-size:12px; padding:6px;\">${engT('eng_no_focus')}</div>`;\n"
    "              const _monthHeader = `<div class=\"pcard-prod-window\">\n"
    "                <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"5\" width=\"18\" height=\"16\" rx=\"2\"/><path d=\"M3 10h18M8 3v4M16 3v4\"/></svg>\n"
    "                <span>${engT('pal_tracked_over')} <b>${engT('pal_month_may')} + ${engT('pal_month_june')}</b></span>\n"
    "              </div>`;\n"
    "              const sM1 = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M1);\n",
    'expanded products list: month-coverage header')

# Then emit _monthHeader before the sorted product list. The current code
# returns `sorted.map(...).join('')`. We change it to prepend _monthHeader.
src = go(src,
    "              return sorted.map(code => {\n",
    "              return _monthHeader + sorted.map(code => {\n",
    'expanded products list: prepend month header')


# ---- 6) i18n keys -----------------------------------------------------
def add_after(s, anchor, addition, label):
    o = anchor.replace('\n', nl)
    n = o + addition.replace('\n', nl)
    if n in s and o not in s: print('  [skip] ' + label); return s
    if o not in s: print('  [FAIL] ' + label); sys.exit(2)
    if s.count(o) != 1: print('  [FAIL] ' + label + ' (count ' + str(s.count(o)) + ')'); sys.exit(2)
    print('  [ok]   ' + label)
    return s.replace(o, n, 1)

src = add_after(src,
    "    pal_setup_banner_t: '{n} client(s) sans produits engagés', pal_setup_banner_d: 'Pour chaque zbon, sélectionnez ≥10 produits parmi la liste focus.', pal_setup_banner_cta: 'Configurer maintenant →',\n",
    "    pal_month_may: 'Mai 2026', pal_month_june: 'Juin 2026',\n"
    "    pal_campaign_window: 'Campagne', pal_tracked_over: 'Suivi sur',\n",
    'FR pal_month_may/june + campaign_window + tracked_over')

src = add_after(src,
    "    pal_setup_banner_t: '{n} client(s) without committed products', pal_setup_banner_d: 'For each client, pick ≥10 products from the focus list.', pal_setup_banner_cta: 'Set up now →',\n",
    "    pal_month_may: 'May 2026', pal_month_june: 'June 2026',\n"
    "    pal_campaign_window: 'Campaign', pal_tracked_over: 'Tracked over',\n",
    'EN pal_month_may/june + campaign_window + tracked_over')

src = add_after(src,
    "    pal_setup_banner_t: '{n} زبون بدون منتجات ملتزم بها', pal_setup_banner_d: 'لكل زبون، اختر 10 منتجات على الأقل من القائمة.', pal_setup_banner_cta: 'بدء الإعداد ←',\n",
    "    pal_month_may: 'ماي 2026', pal_month_june: 'يونيو 2026',\n"
    "    pal_campaign_window: 'الحملة', pal_tracked_over: 'متتبع على',\n",
    'AR pal_month_may/june + campaign_window + tracked_over')


io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
