#!/usr/bin/env python3
"""Phase 1: Hide upload tiles + sync controls for non-creators.

Targets and date range stay per-user (everyone can edit their own).
Phase 2 (shared data reads) is a follow-up patch.
"""
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
    if "GMV_CREATOR_EMAIL" in src:
        print("[skip] already done"); return

    # 1) Constants + helper at the top of the GMV module.
    helper = (
        "// =========================================================================\n"
        "// Roles: only the creator can upload files. Everyone else sees the data.\n"
        "// Targets and date range remain per-user.\n"
        "// =========================================================================\n"
        "const GMV_CREATOR_EMAIL = 'ahmed.mouatamid@z.systems';\n"
        "function gmvIsCreator() {\n"
        "  return !!(sbUser && sbUser.email && sbUser.email.toLowerCase() === GMV_CREATOR_EMAIL.toLowerCase());\n"
        "}\n"
        "// Hide the upload tiles + sync controls for viewers. Re-run on auth change.\n"
        "function gmvApplyRoleUI() {\n"
        "  const isCreator = gmvIsCreator();\n"
        "  const strip = document.getElementById('gmvDsStrip');\n"
        "  if (strip) strip.style.display = isCreator ? '' : 'none';\n"
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
        "}\n"
        "\n"
    )
    src = must_replace_once(src, "const GMV_LS_TARGETS = 'rihab_gmv_targets_v1';", helper + "const GMV_LS_TARGETS = 'rihab_gmv_targets_v1';", "helper block")

    # 2) Block the upload handlers for non-creators (defense in depth).
    for fn_anchor in [
        "async function gmvOnUploadClients(e) {\n  const f = e.target.files && e.target.files[0]; if (!f) return;",
        "async function gmvOnUploadOrders(e) {\n  const f = e.target.files && e.target.files[0]; if (!f) return;",
        "async function gmvOnUploadCategories(e) {\n  const f = e.target.files && e.target.files[0]; if (!f) return;",
    ]:
        guard = "  if (!gmvIsCreator()) { alert('Only the creator can upload files. You\\u2019re in viewer mode.'); try { e.target.value = ''; } catch (_) {} return; }\n"
        replacement = fn_anchor + "\n" + guard
        src = must_replace_once(src, fn_anchor, replacement, "guard for " + fn_anchor[:40])

    # 3) Call gmvApplyRoleUI() at the end of gmvInit.
    old_init_end = "  gmvRenderAll();\n  gmvRenderAuthChip();\n  gmvRefreshSyncBtn();"
    new_init_end = "  gmvRenderAll();\n  gmvRenderAuthChip();\n  gmvRefreshSyncBtn();\n  try { gmvApplyRoleUI(); } catch (_) {}"
    src = must_replace_once(src, old_init_end, new_init_end, "init call")

    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(src)
    print("[OK] Phase 1 done.")
    print("    • Creator email: " + "ahmed.mouatamid@z.systems")
    print("    • Viewers: upload tiles hidden, blue 'Viewer mode' badge shown.")
    print("    • Targets stay per-user.")
    print("\nTo change creator: edit GMV_CREATOR_EMAIL near the top of the GMV module.")

if __name__ == '__main__':
    main()
