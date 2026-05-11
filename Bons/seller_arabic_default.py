# -*- coding: utf-8 -*-
"""
Make Arabic the always-on default for sellers.

The previous pickDefault() honored ANY of three legacy localStorage
keys as "explicit choice", including the legacy planner / OF per-feature
keys (rihab_lang_v1 / rihab_ff_lang_v1). That meant a seller who had
ever interacted with the old Planner FR/EN toggle was stuck on a
non-Arabic default even though they never used the new global switcher.

Fix: ONLY `rihab_app_lang_v1` counts as the explicit choice from the
unified switcher. For sellers, no explicit choice → Arabic.
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

# 1) Only the unified switcher key counts as an explicit choice.
src = go(src,
    "  // Decide the default once: explicit user choice > seller-default > en.\n"
    "  function pickDefault() {\n"
    "    try {\n"
    "      var saved = localStorage.getItem(\"rihab_app_lang_v1\")\n"
    "               || localStorage.getItem(\"rihab_ff_lang_v1\")\n"
    "               || localStorage.getItem(\"rihab_lang_v1\");\n"
    "      if (saved === \"fr\" || saved === \"en\" || saved === \"ar\") return saved;\n"
    "    } catch (_) {}\n"
    "    try {\n"
    "      if (typeof gmvSellerName === \"function\" && gmvSellerName()) return \"ar\";\n"
    "    } catch (_) {}\n"
    "    return \"en\";\n"
    "  }\n",
    "  // Pick the default language:\n"
    "  //   1. The unified switcher choice (rihab_app_lang_v1) wins — ONLY this\n"
    "  //      key counts as an explicit user action. Legacy per-feature keys\n"
    "  //      (rihab_lang_v1, rihab_ff_lang_v1) used to be read here, but they\n"
    "  //      get set by side-effects of other code paths and would override\n"
    "  //      the seller default, which we don't want.\n"
    "  //   2. Sellers (gmvSellerName() truthy) default to Arabic.\n"
    "  //   3. Everyone else defaults to English.\n"
    "  function pickDefault() {\n"
    "    try {\n"
    "      var saved = localStorage.getItem(\"rihab_app_lang_v1\");\n"
    "      if (saved === \"fr\" || saved === \"en\" || saved === \"ar\") return saved;\n"
    "    } catch (_) {}\n"
    "    try {\n"
    "      if (typeof gmvSellerName === \"function\" && gmvSellerName()) return \"ar\";\n"
    "    } catch (_) {}\n"
    "    return \"en\";\n"
    "  }\n",
    'pickDefault: only honor rihab_app_lang_v1 as explicit choice')

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
