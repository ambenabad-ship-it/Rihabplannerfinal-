# -*- coding: utf-8 -*-
"""
Add a global language switcher to the app header.

Goal: every signed-in user (creator, viewer, seller) sees a small FR/EN/AR
pill switcher fixed at the top-right of the page on every feature.
Default: Arabic for sellers, English for everyone else.

What this rewires:
  * Adds a fixed top-right `#appLangSwitch` button group with three pills.
  * Adds `appSetLang(lang)` that:
      - persists to localStorage (both the planner key and the FF/engagement key)
      - sets <html lang/dir>
      - drives the planner's setLanguage() when lang in {en, fr}
      - drives fulfill.lang / fulfillApplyLang() when initialized
      - re-renders GMV/Engagement when visible
      - updates active-pill state
  * Adds boot logic that picks the default lang per role when no choice is saved.
  * Fixes fulfillSetLang() to accept 'ar' (it was clamping to fr|en, dropping AR).

Run:
  python add_global_lang_switch.py

Idempotent. Safe to re-run.
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
CSS_BEGIN = '/* === GLOBAL LANG SWITCH — add_global_lang_switch.py === */'
CSS_END   = '/* === END GLOBAL LANG SWITCH === */'
JS_BEGIN  = '/* GLS_BEGIN */'
JS_END    = '/* GLS_END */'
HTML_MARKER = '<!-- GLS_BUTTON -->'


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


def strip_block(src, begin, end, indent_chars=2):
    """Remove a previously-injected marker block so we can re-add cleanly."""
    if begin not in src or end not in src:
        return src, False
    a = src.index(begin)
    b = src.index(end) + len(end)
    e = b
    while e < len(src) and src[e] in ('\n', '\r'):
        e += 1
    s = a
    if indent_chars and s >= indent_chars and src[s-indent_chars:s] == ' ' * indent_chars:
        s -= indent_chars
    while s > 0 and src[s-1] in ('\n', '\r'):
        s -= 1
    return src[:s] + src[e:], True


CSS_BLOCK = (
    CSS_BEGIN + '\n'
    '  .app-lang-switch {\n'
    '    position: fixed;\n'
    '    top: calc(env(safe-area-inset-top, 0px) + 12px);\n'
    '    right: calc(env(safe-area-inset-right, 0px) + 12px);\n'
    '    z-index: 1002;\n'
    '    display: inline-flex;\n'
    '    background: #fff;\n'
    '    border: 1px solid #e2e8f0;\n'
    '    border-radius: 8px;\n'
    '    overflow: hidden;\n'
    '    box-shadow: 0 1px 3px rgba(15, 23, 42, .08);\n'
    '    font-size: 11px;\n'
    '    font-weight: 600;\n'
    '  }\n'
    '  .app-lang-switch button {\n'
    '    border: 0;\n'
    '    background: transparent;\n'
    '    color: #475569;\n'
    '    padding: 6px 10px;\n'
    '    cursor: pointer;\n'
    '    min-width: 36px;\n'
    '    line-height: 1;\n'
    '    transition: background-color .12s, color .12s;\n'
    '    font: inherit;\n'
    '  }\n'
    '  .app-lang-switch button:hover { background: #f1f5f9; color: #0f172a; }\n'
    '  .app-lang-switch button.active { background: #0f172a; color: #fff; }\n'
    '  .app-lang-switch button + button { border-left: 1px solid #e2e8f0; }\n'
    '  body.is-locked .app-lang-switch { display: none; }\n'
    '  @media (max-width: 768px) {\n'
    '    .app-lang-switch { font-size: 10px; }\n'
    '    .app-lang-switch button { padding: 6px 8px; min-width: 32px; }\n'
    '  }\n'
    + CSS_END
)


# The HTML element — inserted just before #appShell so it's a body-level
# fixed sibling. Marker comment makes it idempotent.
HTML_INSERT = (
    HTML_MARKER + '\n'
    '<div class="app-lang-switch" id="appLangSwitch" role="group" aria-label="Language">\n'
    '  <button type="button" data-applang="fr">FR</button>\n'
    '  <button type="button" data-applang="en">EN</button>\n'
    '  <button type="button" data-applang="ar">عربي</button>\n'
    '</div>\n'
)


# JS block — wires the switch + provides the unified setter + boot defaults.
JS_BLOCK = (
    JS_BEGIN + '\n'
    '(function () {\n'
    '  // Unified language setter that drives every i18n surface in the app:\n'
    '  //   1. Planner (data-i18n) — only knows en/fr; ar collapses to en.\n'
    '  //   2. Order Fulfillment / Engagement / GMV — fulfill.lang, fr/en/ar.\n'
    '  //   3. Document <html lang/dir> for RTL.\n'
    '  function appSetLang(next) {\n'
    '    if (next !== "fr" && next !== "en" && next !== "ar") next = "en";\n'
    '    // 1) Persist to both legacy keys so any feature that reads either picks it up.\n'
    '    try {\n'
    '      localStorage.setItem("rihab_app_lang_v1", next);\n'
    '      // Planner clamps to en/fr.\n'
    '      var plannerLang = (next === "fr") ? "fr" : "en";\n'
    '      localStorage.setItem("rihab_lang_v1", plannerLang);\n'
    '      // OF/Engagement carry full fr/en/ar.\n'
    '      localStorage.setItem("rihab_ff_lang_v1", next);\n'
    '    } catch (_) {}\n'
    '    // 2) Update <html lang/dir>.\n'
    '    try {\n'
    '      document.documentElement.lang = next;\n'
    '      document.documentElement.dir  = (next === "ar") ? "rtl" : "ltr";\n'
    '    } catch (_) {}\n'
    '    // 3) Drive Planner i18n if its setter is loaded.\n'
    '    try {\n'
    '      if (typeof setLanguage === "function") {\n'
    '        setLanguage((next === "fr") ? "fr" : "en");\n'
    '      }\n'
    '    } catch (_) {}\n'
    '    // 4) Drive Order Fulfillment / Engagement / GMV.\n'
    '    try {\n'
    '      if (typeof fulfill !== "undefined" && fulfill) {\n'
    '        fulfill.lang = next;\n'
    '        if (typeof fulfillApplyLang === "function") fulfillApplyLang();\n'
    '      }\n'
    '    } catch (_) {}\n'
    '    // 5) Re-render GMV / Engagement when visible.\n'
    '    try {\n'
    '      var gmvFeat = document.getElementById("featureGmvMaker");\n'
    '      if (gmvFeat && gmvFeat.style.display !== "none") {\n'
    '        if (typeof gmvRenderAll === "function") gmvRenderAll();\n'
    '        else if (typeof gmvRenderResults === "function") gmvRenderResults();\n'
    '      }\n'
    '    } catch (_) {}\n'
    '    // 6) Update active-pill state on every visible switcher\n'
    '    //    (the global one + any in-feature ones still in the DOM).\n'
    '    document.querySelectorAll("#appLangSwitch button[data-applang]").forEach(function (b) {\n'
    '      b.classList.toggle("active", b.getAttribute("data-applang") === next);\n'
    '    });\n'
    '    document.querySelectorAll(".ff-lang-btn[data-fflang]").forEach(function (b) {\n'
    '      var on = b.getAttribute("data-fflang") === next;\n'
    '      b.classList.toggle("active", on);\n'
    '      if (b.style) {\n'
    '        b.style.background = on ? "#0f172a" : "#fff";\n'
    '        b.style.color = on ? "#fff" : "#475569";\n'
    '      }\n'
    '    });\n'
    '    document.querySelectorAll(".lang-btn[data-lang]").forEach(function (b) {\n'
    '      var on = b.getAttribute("data-lang") === ((next === "fr") ? "fr" : "en");\n'
    '      b.classList.toggle("active", on);\n'
    '    });\n'
    '  }\n'
    '  window.appSetLang = appSetLang;\n'
    '\n'
    '  // Decide the default once: explicit user choice > seller-default > en.\n'
    '  function pickDefault() {\n'
    '    try {\n'
    '      var saved = localStorage.getItem("rihab_app_lang_v1")\n'
    '               || localStorage.getItem("rihab_ff_lang_v1")\n'
    '               || localStorage.getItem("rihab_lang_v1");\n'
    '      if (saved === "fr" || saved === "en" || saved === "ar") return saved;\n'
    '    } catch (_) {}\n'
    '    try {\n'
    '      if (typeof gmvSellerName === "function" && gmvSellerName()) return "ar";\n'
    '    } catch (_) {}\n'
    '    return "en";\n'
    '  }\n'
    '\n'
    '  // Wire the switcher buttons.\n'
    '  document.addEventListener("click", function (e) {\n'
    '    var btn = e.target && e.target.closest && e.target.closest("#appLangSwitch button[data-applang]");\n'
    '    if (!btn) return;\n'
    '    appSetLang(btn.getAttribute("data-applang"));\n'
    '  });\n'
    '\n'
    '  // Apply initial language once the page settles. Re-apply after auth\n'
    '  // resolves (a seller signing in late should flip to Arabic if they\n'
    '  // never chose another language).\n'
    '  function applyInitial() {\n'
    '    try { appSetLang(pickDefault()); } catch (_) {}\n'
    '  }\n'
    '  if (document.readyState === "loading") {\n'
    '    document.addEventListener("DOMContentLoaded", applyInitial);\n'
    '  } else {\n'
    '    setTimeout(applyInitial, 0);\n'
    '  }\n'
    '  try {\n'
    '    if (typeof sb !== "undefined" && sb && sb.auth) {\n'
    '      sb.auth.onAuthStateChange(function () {\n'
    '        // Only auto-flip if the user has not made an explicit choice yet.\n'
    '        try {\n'
    '          if (!localStorage.getItem("rihab_app_lang_v1")) applyInitial();\n'
    '        } catch (_) {}\n'
    '      });\n'
    '    }\n'
    '  } catch (_) {}\n'
    '})();\n'
    + JS_END
)


def main():
    print('Patching: ' + INDEX_PATH)
    src = read_file(INDEX_PATH)
    nl = '\r\n' if '\r\n' in src else '\n'

    # ---- 1) CSS block ----------------------------------------------------
    src, _ = (lambda r: r if r[1] else (r[0], False))(strip_block(src, CSS_BEGIN, CSS_END))
    css_anchor = nl + '  /* RTL fine-tuning for Arabic */' + nl
    if css_anchor not in src:
        print('  [FAIL] CSS anchor not found')
        sys.exit(2)
    src = src.replace(css_anchor, nl + '  ' + CSS_BLOCK.replace('\n', nl) + nl + css_anchor, 1)
    print('  [ok]   injected CSS')

    # ---- 2) HTML element -------------------------------------------------
    if HTML_MARKER not in src:
        html_anchor = '<div class="app-shell" id="appShell">'
        if html_anchor not in src:
            print('  [FAIL] HTML anchor not found')
            sys.exit(2)
        src = src.replace(
            html_anchor,
            HTML_INSERT.replace('\n', nl) + html_anchor,
            1,
        )
        print('  [ok]   inserted lang switch HTML')
    else:
        print('  [skip] lang switch HTML (already inserted)')

    # ---- 3) JS init block ------------------------------------------------
    if JS_BEGIN in src and JS_END in src:
        a = src.index(JS_BEGIN)
        b = src.index(JS_END) + len(JS_END)
        e = b
        while e < len(src) and src[e] in ('\n', '\r'):
            e += 1
        s = a
        while s > 0 and src[s-1] in ('\n', '\r'):
            s -= 1
        src = src[:s] + src[e:]
        print('  [ok]   removed previous JS block')

    # Inject the JS at the end of the file just before </body>.
    js_anchor = '</body>'
    if js_anchor not in src:
        print('  [FAIL] could not find </body> anchor')
        sys.exit(2)
    if src.count(js_anchor) > 1:
        print('  [warn] multiple </body> tags; using the last one')
        last = src.rfind(js_anchor)
        src = src[:last] + nl + '<script>' + nl + JS_BLOCK.replace('\n', nl) + nl + '</script>' + nl + src[last:]
    else:
        src = src.replace(js_anchor, nl + '<script>' + nl + JS_BLOCK.replace('\n', nl) + nl + '</script>' + nl + js_anchor, 1)
    print('  [ok]   injected JS init block')

    # ---- 4) Fix fulfillSetLang to accept 'ar' --------------------------
    old_set = (
        "function fulfillSetLang(lang) {\n"
        "  fulfill.lang = (lang === 'en') ? 'en' : 'fr';\n"
        "  try { localStorage.setItem('rihab_ff_lang_v1', fulfill.lang); } catch (_) {}\n"
        "  fulfillApplyLang();\n"
        "}\n"
    )
    new_set = (
        "function fulfillSetLang(lang) {\n"
        "  // Delegate to the unified switcher so every surface stays in sync.\n"
        "  if (typeof window.appSetLang === 'function') { window.appSetLang(lang); return; }\n"
        "  fulfill.lang = (lang === 'en' || lang === 'ar') ? lang : 'fr';\n"
        "  try { localStorage.setItem('rihab_ff_lang_v1', fulfill.lang); } catch (_) {}\n"
        "  fulfillApplyLang();\n"
        "}\n"
    )
    src, _ = replace_once(src, old_set, new_set,
                          'fulfillSetLang accepts ar + delegates to appSetLang', nl)

    write_file(INDEX_PATH, src)
    print('Done.')


if __name__ == '__main__':
    main()
