# -*- coding: utf-8 -*-
"""
Phase 2 viewer reads — comprehensive fix.

Bugs addressed:
  #1 gmvPullClientsFromSupabaseIfNeeded reads via sbReadKey (own user)
     instead of gmvReadShared (creator for viewers).
  #2 The manual "Pull from my account" button reads clients/orders/names
     via sbReadKey (own user). Should use gmvReadShared.
  #3 Force-pull's order mapper drops `productCode`, and force-pull never
     reads `gmv_categories` at all.
  #4 sbReadKeyAs swallows errors silently; viewers can't tell when an
     RLS read fails. Inject a small UI banner so the failure surfaces.

Run:
  python fix_phase2_viewer_reads.py

Idempotent. Each replacement uses a unique anchor (the file has many
similar-looking blocks, so anchors are intentionally large).
"""

import io
import os
import sys

# Locate index.html. Prefer an explicit CLI arg; otherwise probe the
# usual Windows layout (Bons sibling of "Rehab app ( planner) - Copie")
# and the Linux session mount layout.
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
    print('Pass the path as an argument: '
          'python fix_phase2_viewer_reads.py "C:\\\\path\\\\to\\\\index.html"')
    sys.exit(1)


INDEX_PATH = _find_index()


def read_file(path):
    with io.open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def write_file(path, content):
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)


def replace_once(src, old, new, label):
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


def main():
    print('Patching: ' + INDEX_PATH)
    src = read_file(INDEX_PATH)

    # ---- Fix #1: gmv_clients auto-pull -> gmvReadShared --------------
    old1 = (
        "async function gmvPullClientsFromSupabaseIfNeeded() {\n"
        "  if (gmv.clients && Object.keys(gmv.clients).length > 0) return;\n"
        "  if (!sbUser || typeof sbReadKey !== 'function') return;\n"
        "  try {\n"
        "    const cloud = await sbReadKey('gmv_clients');\n"
    )
    new1 = (
        "async function gmvPullClientsFromSupabaseIfNeeded() {\n"
        "  if (gmv.clients && Object.keys(gmv.clients).length > 0) return;\n"
        "  if (!sbUser || typeof sbReadKey !== 'function') return;\n"
        "  try {\n"
        "    const cloud = await gmvReadShared('gmv_clients');\n"
    )
    src, _ = replace_once(src, old1, new1,
                          'Fix #1 gmvPullClientsFromSupabaseIfNeeded')

    # ---- Fix #2 + #3: force-pull button (clients/orders/names + cats) -
    old2 = (
        "        // Force-pull all GMV data from Supabase, replacing local cache.\n"
        "        const [cloudClients, cloudOrders, cloudNames, cloudTargets] = await Promise.all([\n"
        "          sbReadKey('gmv_clients'),\n"
        "          sbReadKey('gmv_orders'),\n"
        "          sbReadKey('gmv_names'),\n"
        "          sbReadKey('gmv_targets'),\n"
        "        ]);\n"
    )
    new2 = (
        "        // Force-pull all GMV data from Supabase, replacing local cache.\n"
        "        // Viewers read from creator via gmvReadShared; targets stay per-user.\n"
        "        const [cloudClients, cloudOrders, cloudNames, cloudCategories, cloudTargets] = await Promise.all([\n"
        "          gmvReadShared('gmv_clients'),\n"
        "          gmvReadShared('gmv_orders'),\n"
        "          gmvReadShared('gmv_names'),\n"
        "          gmvReadShared('gmv_categories'),\n"
        "          sbReadKey('gmv_targets'),\n"
        "        ]);\n"
    )
    src, _ = replace_once(src, old2, new2,
                          'Fix #2 force-pull reads use gmvReadShared')

    # Add productCode back into the order mapper used by force-pull.
    old3 = (
        "          gmv.orders = cloudOrders.map(o => ({\n"
        "            phone: o.phone,\n"
        "            date: o.date ? new Date(o.date) : null,\n"
        "            amount: typeof o.amount === 'number' ? o.amount : parseFloat(o.amount) || 0,\n"
        "            status: gmvNormStatus(o.status || ''),\n"
        "            store: o.store || ''\n"
        "          })).filter(o => o.phone && o.date && o.status && GMV_STATUSES.indexOf(o.status) >= 0);\n"
    )
    new3 = (
        "          gmv.orders = cloudOrders.map(o => ({\n"
        "            phone: o.phone,\n"
        "            date: o.date ? new Date(o.date) : null,\n"
        "            amount: typeof o.amount === 'number' ? o.amount : parseFloat(o.amount) || 0,\n"
        "            status: gmvNormStatus(o.status || ''),\n"
        "            store: o.store || '',\n"
        "            productCode: o.productCode || ''\n"
        "          })).filter(o => o.phone && o.date && o.status && GMV_STATUSES.indexOf(o.status) >= 0);\n"
    )
    src, _ = replace_once(src, old3, new3,
                          'Fix #3a force-pull mapper now keeps productCode')

    # Insert categories handling right after the cloudTargets block in
    # the force-pull handler. Anchor: the targets block followed by the
    # "nothing found / pulled" status update block.
    old4 = (
        "        if (cloudTargets && typeof cloudTargets === 'object') {\n"
        "          gmv.targets = cloudTargets;\n"
        "          gmvMigrateLegacyTargets();\n"
        "          try { saveJSON(GMV_LS_TARGETS, gmv.targets); } catch (_) {}\n"
        "        }\n"
        "        if (nC === 0 && nO === 0) {\n"
    )
    new4 = (
        "        if (cloudTargets && typeof cloudTargets === 'object') {\n"
        "          gmv.targets = cloudTargets;\n"
        "          gmvMigrateLegacyTargets();\n"
        "          try { saveJSON(GMV_LS_TARGETS, gmv.targets); } catch (_) {}\n"
        "        }\n"
        "        if (cloudCategories && typeof cloudCategories === 'object') {\n"
        "          gmv.productCategories = cloudCategories;\n"
        "          try { saveJSON(GMV_LS_CATEGORIES, cloudCategories); } catch (_) {}\n"
        "        }\n"
        "        if (nC === 0 && nO === 0) {\n"
    )
    src, _ = replace_once(src, old4, new4,
                          'Fix #3b force-pull now hydrates productCategories')

    # ---- Fix #4: surface RLS errors in viewer UI ---------------------
    # Replace sbReadKeyAs body to track last error on window, and inject
    # a banner from gmvApplyRoleUI when the flag is set for viewers.
    old5 = (
        "async function sbReadKeyAs(userId, key) {\n"
        "  if (!sb || !userId) return null;\n"
        "  const { data, error } = await sb.from('user_data')\n"
        "    .select('value').eq('user_id', userId).eq('key', key).maybeSingle();\n"
        "  if (error) { console.warn('sbReadKeyAs', error); return null; }\n"
        "  return data ? data.value : null;\n"
        "}\n"
    )
    new5 = (
        "async function sbReadKeyAs(userId, key) {\n"
        "  if (!sb || !userId) return null;\n"
        "  const { data, error } = await sb.from('user_data')\n"
        "    .select('value').eq('user_id', userId).eq('key', key).maybeSingle();\n"
        "  if (error) {\n"
        "    console.warn('sbReadKeyAs', error);\n"
        "    try {\n"
        "      window.__gmvSharedReadError = {\n"
        "        key: key,\n"
        "        message: (error && error.message) ? error.message : String(error),\n"
        "        when: Date.now()\n"
        "      };\n"
        "      if (typeof gmvApplyRoleUI === 'function') gmvApplyRoleUI();\n"
        "    } catch (_) {}\n"
        "    return null;\n"
        "  }\n"
        "  return data ? data.value : null;\n"
        "}\n"
    )
    src, _ = replace_once(src, old5, new5,
                          'Fix #4a sbReadKeyAs records read errors')

    # Inject error-banner branch into gmvApplyRoleUI right before its
    # closing brace. Anchor: the trailing "} else if (badge) ..." block
    # plus the function's closing brace.
    old6 = (
        "  } else if (badge) {\n"
        "    badge.remove();\n"
        "  }\n"
        "}\n"
        "\n"
        "const GMV_LS_TARGETS = 'rihab_gmv_targets_v1';\n"
    )
    new6 = (
        "  } else if (badge) {\n"
        "    badge.remove();\n"
        "  }\n"
        "  // Surface shared-read failures (typically a missing/incorrect\n"
        "  // Supabase RLS policy) so viewers know why nothing renders.\n"
        "  try {\n"
        "    const errInfo = window.__gmvSharedReadError;\n"
        "    let errBanner = document.getElementById('gmvSharedReadErrorBanner');\n"
        "    if (!isCreator && sbUser && errInfo) {\n"
        "      if (!errBanner) {\n"
        "        errBanner = document.createElement('div');\n"
        "        errBanner.id = 'gmvSharedReadErrorBanner';\n"
        "        errBanner.style.cssText = 'margin:0 0 12px; padding:10px 14px; border-radius:6px; background:#fee2e2; color:#7f1d1d; font-size:12px; border:1px solid #fecaca;';\n"
        "        const host = document.getElementById('gmvWrap') || document.querySelector('.gmv-wrap') || document.body;\n"
        "        if (host && host.firstChild) host.insertBefore(errBanner, host.firstChild);\n"
        "        else if (host) host.appendChild(errBanner);\n"
        "      }\n"
        "      errBanner.innerHTML = '<b>Cannot read shared data</b> \\u2014 key <code>' + errInfo.key + '</code>: ' + errInfo.message + '. Likely the Supabase RLS policy that lets viewers read the creator\\u2019s row is missing or scoped wrong. Ask the creator to re-apply the policy from HANDOFF.md.';\n"
        "    } else if (errBanner) {\n"
        "      errBanner.remove();\n"
        "    }\n"
        "  } catch (_) {}\n"
        "}\n"
        "\n"
        "const GMV_LS_TARGETS = 'rihab_gmv_targets_v1';\n"
    )
    src, _ = replace_once(src, old6, new6,
                          'Fix #4b gmvApplyRoleUI shows RLS error banner')

    write_file(INDEX_PATH, src)
    print('Done.')


if __name__ == '__main__':
    main()
