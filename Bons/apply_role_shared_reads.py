#!/usr/bin/env python3
"""Phase 2: viewers read clients/orders/names/categories from the creator's user_data row."""
import os, sys
TARGET = r"C:\Users\KamalSAGUEM\OneDrive - Beyond believers\Bureau\Rehab app ( planner) - Copie\rigab_app\index.html"

def must_replace_once(src, anchor, replacement, label):
    n = src.count(anchor)
    if n == 0: raise SystemExit("[FAIL] anchor not found for " + label)
    if n > 1:  raise SystemExit("[FAIL] anchor appears " + str(n) + "x for " + label)
    return src.replace(anchor, replacement, 1)

def main():
    with open(TARGET, 'r', encoding='utf-8') as f:
        src = f.read()
    if "GMV_CREATOR_USER_ID" in src:
        print("[skip] already done"); return

    # 1) Add creator UUID constant + helpers right after gmvIsCreator.
    helper = (
        "// ---- Phase 2: viewers read creator's GMV data ----\n"
        "// Paste the creator's Supabase user UUID here (one time). To find it:\n"
        "//   Sign in as the creator, open browser console, type sbUser.id\n"
        "// Or check Supabase dashboard \\u2192 Authentication \\u2192 Users.\n"
        "// While this is empty, viewers fall back to their own (empty) data.\n"
        "const GMV_CREATOR_USER_ID = '';\n"
        "\n"
        "// Read a user_data row by user_id (defaults to current user).\n"
        "async function sbReadKeyAs(userId, key) {\n"
        "  if (!sb || !userId) return null;\n"
        "  const { data, error } = await sb.from('user_data')\n"
        "    .select('value').eq('user_id', userId).eq('key', key).maybeSingle();\n"
        "  if (error) { console.warn('sbReadKeyAs', error); return null; }\n"
        "  return data ? data.value : null;\n"
        "}\n"
        "\n"
        "// For shared keys, viewers read from creator; creator reads from self.\n"
        "function gmvDataSourceUserId() {\n"
        "  if (!sbUser) return null;\n"
        "  if (gmvIsCreator()) return sbUser.id;\n"
        "  return GMV_CREATOR_USER_ID || sbUser.id;\n"
        "}\n"
        "async function gmvReadShared(key) {\n"
        "  const uid = gmvDataSourceUserId();\n"
        "  return sbReadKeyAs(uid, key);\n"
        "}\n"
        "\n"
    )
    src = must_replace_once(src, "function gmvIsCreator() {", helper + "function gmvIsCreator() {", "helpers")

    # 2) Replace gmvPullClientsFromSupabaseIfNeeded / Orders / Categories to use shared read for non-creator.
    # Find each pull function and swap sbReadKey('gmv_*') -> gmvReadShared('gmv_*').
    # Clients pull
    src = src.replace(
        "    const cloudClients = await sbReadKey('gmv_clients');",
        "    const cloudClients = await gmvReadShared('gmv_clients');",
        1
    )
    # Orders pull
    src = src.replace(
        "    const cloudOrders = await sbReadKey('gmv_orders');",
        "    const cloudOrders = await gmvReadShared('gmv_orders');",
        1
    )
    src = src.replace(
        "    const cloudNames = await sbReadKey('gmv_names');",
        "    const cloudNames = await gmvReadShared('gmv_names');",
        1
    )
    # Categories pull
    src = src.replace(
        "    const cloudCats = await sbReadKey('gmv_categories');",
        "    const cloudCats = await gmvReadShared('gmv_categories');",
        1
    )

    # 3) Show the creator their UUID so they can paste it (visible only to creator).
    role_ui_old = (
        "function gmvApplyRoleUI() {\n"
        "  const isCreator = gmvIsCreator();\n"
        "  const strip = document.getElementById('gmvDsStrip');\n"
        "  if (strip) strip.style.display = isCreator ? '' : 'none';"
    )
    role_ui_new = (
        "function gmvApplyRoleUI() {\n"
        "  const isCreator = gmvIsCreator();\n"
        "  const strip = document.getElementById('gmvDsStrip');\n"
        "  if (strip) strip.style.display = isCreator ? '' : 'none';\n"
        "  // Creator: show their UUID so they can paste it into GMV_CREATOR_USER_ID + the SQL policy.\n"
        "  if (isCreator && sbUser && !GMV_CREATOR_USER_ID) {\n"
        "    let cBanner = document.getElementById('gmvCreatorIdBanner');\n"
        "    if (!cBanner) {\n"
        "      cBanner = document.createElement('div');\n"
        "      cBanner.id = 'gmvCreatorIdBanner';\n"
        "      cBanner.style.cssText = 'margin:0 0 12px; padding:10px 14px; border-radius:6px; background:#fef3c7; color:#92400e; font-size:12px; border:1px solid #fde68a;';\n"
        "      cBanner.innerHTML = '<b>Creator UUID:</b> <code style=\"user-select:all; background:#fff; padding:2px 6px; border-radius:3px;\">' + sbUser.id + '</code> \\u2014 paste this into <code>GMV_CREATOR_USER_ID</code> in index.html (and into the Supabase SQL policy), then this banner goes away.';\n"
        "      const host = document.getElementById('gmvWrap') || document.querySelector('.gmv-wrap') || document.body;\n"
        "      if (host && host.firstChild) host.insertBefore(cBanner, host.firstChild);\n"
        "    }\n"
        "  }"
    )
    src = must_replace_once(src, role_ui_old, role_ui_new, "creator banner")

    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] Phase 2 patch applied.")
    print()
    print("=" * 70)
    print("NEXT 2 STEPS (one-time):")
    print("=" * 70)
    print()
    print("STEP A: get the creator's UUID")
    print("  1. Sign in as ahmed.mouatamid@z.systems")
    print("  2. Hard-refresh the app — a yellow banner shows your UUID at the top")
    print("  3. Copy the UUID")
    print()
    print("STEP B: paste it in TWO places")
    print()
    print("  B1) Edit index.html, find the line:")
    print("        const GMV_CREATOR_USER_ID = '';")
    print("      and paste your UUID:")
    print("        const GMV_CREATOR_USER_ID = '<paste-here>';")
    print()
    print("  B2) Run this SQL once in Supabase \\u2192 SQL Editor")
    print("      (replace <paste-here> with the same UUID):")
    print()
    print("    DROP POLICY IF EXISTS \"viewers read creator gmv\" ON user_data;")
    print("    CREATE POLICY \"viewers read creator gmv\"")
    print("      ON user_data FOR SELECT")
    print("      TO authenticated")
    print("      USING (")
    print("        user_id = '<paste-here>'::uuid")
    print("        AND key IN ('gmv_clients', 'gmv_orders', 'gmv_names', 'gmv_categories')")
    print("      );")
    print()
    print("After both, push to git. Viewers will see your uploaded data.")

if __name__ == '__main__':
    main()
