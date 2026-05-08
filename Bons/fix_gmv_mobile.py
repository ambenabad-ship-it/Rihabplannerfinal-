# -*- coding: utf-8 -*-
"""
GMV Tracker mobile-pass fixes.

Addresses the audit findings on the GMV Tracker page (Arabic, 388px):

  Bug 1  #gmvRoleBadge mounts on <body> -> moves it into .gmv-inner so
         it respects the GMV layout and doesn't push the whole #appShell
         down.
  Bug 2  document.documentElement lang/dir not set when language changes.
  Bug 4  Engagement sub-tabs (focus / paliers / scoreboard) render with
         inline styles and fall apart visually on mobile -> add a proper
         class-based segmented control that looks polished and stays
         visible on dark and light backgrounds.
  Bug 7  cmd-brand mixes 'متتبع' + 'GMV' without bidi isolation -> wrap
         the Latin token in a <bdi>.
  Bug 9  GMV page title not prominent on mobile -> bump cmd-title size
         on phones and dock cmdbar properly under the hamburger.

Skipped (not real bugs):

  Bug 3  Period button hidden on mobile — actually hidden by the seller
         filter in gmvRenderEngagement (sellers don't change periods).
         For viewers it's visible. No fix needed.
  Bug 5  Absolute-positioned 'overflow' div is the radial-gradient halo
         in the personal scoreboard hero. Parent has overflow:hidden,
         and fix_mobile_layout.py already locks body overflow-x:hidden.
  Bug 6  Bottom auth chip overlap — already handled in fix_mobile_layout.
  Bug 8  Planner/Settings sidebar items hidden — intended seller-role
         behaviour. For viewers Planner IS visible; the audit user is a
         seller (Engagement is the only GMV tab showing).

Run:
  python fix_gmv_mobile.py

Idempotent.
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
    print('Could not find index.html. Tried:')
    for c in candidates:
        print('  ' + c)
    sys.exit(1)


INDEX_PATH = _find_index()
MARKER_BEGIN = '/* === GMV MOBILE PASS — fix_gmv_mobile.py === */'
MARKER_END   = '/* === END GMV MOBILE PASS === */'


def read_file(path):
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def write_file(path, content):
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)


def replace_once(src, old, new, label, nl='\n'):
    # Translate \n in the anchor strings to whatever newline style the
    # file is using (CRLF on Windows-checkout files).
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


# CSS additions — class-based engagement sub-tab strip plus the mobile
# cmd-brand bump. Wrapped in a marker block we strip+re-add on rerun.
CSS_BLOCK = (
    MARKER_BEGIN + '\n'
    '  /* Engagement sub-tab segmented control (Bug 4) */\n'
    '  .gmv-engtab-bar {\n'
    '    display: flex;\n'
    '    gap: 4px;\n'
    '    margin: 0 0 14px;\n'
    '    padding: 4px;\n'
    '    background: #f1f5f9;\n'
    '    border-radius: 10px;\n'
    '    box-shadow: inset 0 0 0 1px #e2e8f0;\n'
    '  }\n'
    '  .gmv-engtab {\n'
    '    flex: 1 1 auto;\n'
    '    min-width: 0;\n'
    '    padding: 8px 12px;\n'
    '    border: 0;\n'
    '    background: transparent;\n'
    '    color: #475569;\n'
    '    border-radius: 7px;\n'
    '    font-size: 13px;\n'
    '    font-weight: 600;\n'
    '    cursor: pointer;\n'
    '    text-overflow: ellipsis;\n'
    '    overflow: hidden;\n'
    '    white-space: nowrap;\n'
    '    transition: background-color .15s, color .15s, box-shadow .15s;\n'
    '  }\n'
    '  .gmv-engtab:hover { color: #0f172a; }\n'
    '  .gmv-engtab.active {\n'
    '    background: #0f172a;\n'
    '    color: #fff;\n'
    '    box-shadow: 0 1px 2px rgba(15, 23, 42, .25);\n'
    '  }\n'
    '\n'
    '  /* Role badge — when mounted inside .gmv-inner it inherits page\n'
    '     padding; this is a small polish for spacing + RTL. */\n'
    '  #gmvRoleBadge {\n'
    '    margin: 0 0 12px;\n'
    '    padding: 10px 14px;\n'
    '    border-radius: 8px;\n'
    '    background: #eff6ff;\n'
    '    color: #1e40af;\n'
    '    font-size: 12px;\n'
    '    border: 1px solid #bfdbfe;\n'
    '    line-height: 1.5;\n'
    '  }\n'
    '\n'
    '  @media (max-width: 768px) {\n'
    '    /* Bug 9 — make the page title visible on mobile. */\n'
    '    .gmv-cmdbar { flex-wrap: wrap; padding: 10px 12px; }\n'
    '    .gmv-cmdbar .cmd-title { font-size: 16px; font-weight: 700; }\n'
    '    .gmv-cmdbar .cmd-period { padding: 6px 10px; font-size: 12px; }\n'
    '    .gmv-cmdbar .cmd-period .period-dates { display: none; }\n'
    '    /* Sub-tabs wrap on phones if labels are too long for one row. */\n'
    '    .gmv-engtab-bar { flex-wrap: wrap; }\n'
    '    .gmv-engtab { flex: 1 1 calc(50% - 4px); font-size: 12px; padding: 9px 8px; }\n'
    '    /* Role badge gets a touch more breathing room on mobile. */\n'
    '    #gmvRoleBadge { font-size: 12px; padding: 10px 12px; }\n'
    '  }\n'
    '\n'
    '  /* RTL: flip badge border + ensure cmd-brand reads correctly. */\n'
    '  [dir="rtl"] #gmvRoleBadge { text-align: right; }\n'
    '  .gmv-cmdbar .cmd-brand .cmd-title { unicode-bidi: plaintext; }\n'
    + MARKER_END
)


def main():
    print('Patching: ' + INDEX_PATH)
    src = read_file(INDEX_PATH)
    nl = '\r\n' if '\r\n' in src else '\n'

    # ---- Strip + re-inject CSS marker block ---------------------------
    if MARKER_BEGIN in src and MARKER_END in src:
        a = src.index(MARKER_BEGIN)
        b = src.index(MARKER_END) + len(MARKER_END)
        end = b
        while end < len(src) and src[end] in ('\n', '\r'):
            end += 1
        start = a
        if start >= 2 and src[start-2:start] == '  ':
            start -= 2
        while start > 0 and src[start-1] in ('\n', '\r'):
            start -= 1
        src = src[:start] + src[end:]
        print('  [ok]   removed previous CSS block (re-applying)')

    css_anchor = nl + '  /* RTL fine-tuning for Arabic */' + nl
    if css_anchor not in src:
        print('  [FAIL] could not find CSS anchor')
        sys.exit(2)
    block = CSS_BLOCK.replace('\n', nl)
    src = src.replace(css_anchor, nl + '  ' + block + nl + css_anchor, 1)
    print('  [ok]   injected CSS block')

    # ---- Bug 1 + 2 — role badge target + html lang/dir + i18n --------
    # Replace the badge-creation block to:
    #  - Mount inside .gmv-inner (fall back to body only as last resort)
    #  - Localize text per engLang() and seller/viewer role
    #  - Set <html lang/dir> here too (cheap and runs on every role apply)
    old_badge = (
        "  // Add a small read-only badge so viewers know why uploads are hidden.\n"
        "  let badge = document.getElementById('gmvRoleBadge');\n"
        "  if (!isCreator && sbUser) {\n"
        "    if (!badge) {\n"
        "      badge = document.createElement('div');\n"
        "      badge.id = 'gmvRoleBadge';\n"
        "      badge.style.cssText = 'margin:0 0 12px; padding:8px 12px; border-radius:6px; background:#eff6ff; color:#1e40af; font-size:12px; border:1px solid #bfdbfe;';\n"
        "      badge.textContent = 'Viewer mode \\u2014 you can set your own targets and explore data, but only the creator (' + GMV_CREATOR_EMAIL + ') can upload files.';\n"
        "      const host = document.getElementById('gmvWrap') || document.querySelector('.gmv-wrap') || document.body;\n"
        "      const firstChild = host && host.firstChild;\n"
        "      if (host && firstChild) host.insertBefore(badge, firstChild);\n"
        "      else if (host) host.appendChild(badge);\n"
        "    }\n"
        "  } else if (badge) {\n"
        "    badge.remove();\n"
        "  }\n"
    )
    new_badge = (
        "  // Sync <html lang/dir> with the active engagement language so\n"
        "  // the entire document picks up the right direction (Bug 2).\n"
        "  try {\n"
        "    const _lang = (typeof engLang === 'function') ? engLang() : 'fr';\n"
        "    document.documentElement.lang = _lang;\n"
        "    document.documentElement.dir  = _lang === 'ar' ? 'rtl' : 'ltr';\n"
        "  } catch (_) {}\n"
        "  // Read-only role badge — mounts inside .gmv-inner so it respects\n"
        "  // the page layout (Bug 1) and is localized + role-aware.\n"
        "  let badge = document.getElementById('gmvRoleBadge');\n"
        "  if (!isCreator && sbUser) {\n"
        "    const _lang = (typeof engLang === 'function') ? engLang() : 'fr';\n"
        "    const _isSeller = (typeof gmvIsSeller === 'function') && gmvIsSeller();\n"
        "    const _txt = (() => {\n"
        "      if (_isSeller) {\n"
        "        if (_lang === 'ar') return 'وضع البائع \\u2014 لا يمكنك رفع الملفات. اطلب من المالك (' + GMV_CREATOR_EMAIL + ') رفعها.';\n"
        "        if (_lang === 'en') return 'Seller mode \\u2014 only the creator (' + GMV_CREATOR_EMAIL + ') can upload files. Use the Engagement page to commit your products.';\n"
        "        return 'Mode vendeur \\u2014 seul le créateur (' + GMV_CREATOR_EMAIL + ') peut charger les fichiers. Engagez vos produits depuis la page Engagement.';\n"
        "      }\n"
        "      if (_lang === 'ar') return 'وضع المشاهد \\u2014 يمكنك تحديد أهدافك واستكشاف البيانات، لكن المالك فقط (' + GMV_CREATOR_EMAIL + ') يمكنه رفع الملفات.';\n"
        "      if (_lang === 'en') return 'Viewer mode \\u2014 you can set your own targets and explore data, but only the creator (' + GMV_CREATOR_EMAIL + ') can upload files.';\n"
        "      return 'Mode consultation \\u2014 vous pouvez d\\u00e9finir vos cibles et explorer les donn\\u00e9es, mais seul le cr\\u00e9ateur (' + GMV_CREATOR_EMAIL + ') peut charger les fichiers.';\n"
        "    })();\n"
        "    if (!badge) {\n"
        "      badge = document.createElement('div');\n"
        "      badge.id = 'gmvRoleBadge';\n"
        "    }\n"
        "    badge.textContent = _txt;\n"
        "    badge.setAttribute('dir', _lang === 'ar' ? 'rtl' : 'ltr');\n"
        "    // Mount inside the GMV feature pane, not <body>.\n"
        "    const _gmv = document.getElementById('featureGmvMaker');\n"
        "    const _inner = _gmv ? _gmv.querySelector('.gmv-inner') : null;\n"
        "    const _host = _inner || _gmv || document.getElementById('gmvWrap') || document.querySelector('.gmv-wrap') || document.body;\n"
        "    if (badge.parentNode !== _host) {\n"
        "      if (_host && _host.firstChild) _host.insertBefore(badge, _host.firstChild);\n"
        "      else if (_host) _host.appendChild(badge);\n"
        "    }\n"
        "  } else if (badge) {\n"
        "    badge.remove();\n"
        "  }\n"
    )
    src, _ = replace_once(src, old_badge, new_badge,
                          'Bug 1+2 role badge moves into .gmv-inner + i18n + html lang/dir', nl)

    # ---- Bug 4 — engagement sub-tabs use class-based segmented control
    old_tab = (
        "  const tabBtn = (key, label) => `<button type=\"button\" data-engtab=\"${key}\" style=\"padding:8px 14px; border:0; background:${sub === key ? '#0f172a' : 'transparent'}; color:${sub === key ? '#fff' : '#475569'}; border-radius:6px; font-size:13px; font-weight:600; cursor:pointer;\">${label}</button>`;\n"
    )
    new_tab = (
        "  const tabBtn = (key, label) => `<button type=\"button\" class=\"gmv-engtab${sub === key ? ' active' : ''}\" data-engtab=\"${key}\">${label}</button>`;\n"
    )
    src, _ = replace_once(src, old_tab, new_tab,
                          'Bug 4 engagement sub-tabs use .gmv-engtab class', nl)

    old_bar = (
        "    <div style=\"display:inline-flex; gap:4px; margin:0 0 12px; padding:4px; background:#f1f5f9; border-radius:8px;\">\n"
        "      ${tabBtn('focus', engT('eng_subtab_focus'))}\n"
        "      ${tabBtn('paliers', engT('eng_subtab_paliers'))}\n"
        "      ${tabBtn('scoreboard', engT('eng_subtab_score'))}\n"
        "    </div>\n"
    )
    new_bar = (
        "    <div class=\"gmv-engtab-bar\" role=\"tablist\">\n"
        "      ${tabBtn('focus', engT('eng_subtab_focus'))}\n"
        "      ${tabBtn('paliers', engT('eng_subtab_paliers'))}\n"
        "      ${tabBtn('scoreboard', engT('eng_subtab_score'))}\n"
        "    </div>\n"
    )
    src, _ = replace_once(src, old_bar, new_bar,
                          'Bug 4 engagement sub-tab strip uses .gmv-engtab-bar', nl)

    # ---- Bug 7 — bidi-isolate the cmd-brand title -------------------
    # Wrap the inner title text with <bdi> so 'GMV' renders correctly
    # next to Arabic when a future translation puts Arabic chars in it.
    old_brand = (
        "      <span class=\"cmd-title\">GMV Tracker</span>"
    )
    new_brand = (
        "      <span class=\"cmd-title\" dir=\"auto\"><bdi>GMV Tracker</bdi></span>"
    )
    src, _ = replace_once(src, old_brand, new_brand,
                          'Bug 7 cmd-brand title bidi-isolated', nl)

    # When the cmd-title gets translated dynamically (line 19273-area),
    # wrap the text node with bdi too.
    old_setbrand = (
        "      const titles = { ar: 'متتبع GMV', fr: 'GMV Tracker', en: 'GMV Tracker' };\n"
        "      cmdTitle.textContent = titles[engLang()] || 'GMV Tracker';\n"
    )
    new_setbrand = (
        "      const titles = { ar: 'متتبع GMV', fr: 'GMV Tracker', en: 'GMV Tracker' };\n"
        "      const _t = titles[engLang()] || 'GMV Tracker';\n"
        "      // Use innerHTML with <bdi> so 'GMV' (Latin) is bidi-isolated\n"
        "      // from 'متتبع' (Arabic). Plain text would render confusingly.\n"
        "      cmdTitle.innerHTML = '<bdi>' + _t.replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c])) + '</bdi>';\n"
    )
    src, _ = replace_once(src, old_setbrand, new_setbrand,
                          'Bug 7 cmd-brand i18n wraps in <bdi>', nl)

    write_file(INDEX_PATH, src)
    print('Done.')


if __name__ == '__main__':
    main()
