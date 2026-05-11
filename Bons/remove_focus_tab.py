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

# 1) Default sub-tab to 'paliers' instead of 'focus'.
src = go(src,
    "  activeSubtab: 'focus',\n",
    "  activeSubtab: 'paliers',\n",
    'default activeSubtab -> paliers')

# 2) When activeSubtab is unset, fall back to 'paliers'.
src = go(src,
    "  const sub = gmvEngagement.activeSubtab || 'focus';\n",
    "  const sub = gmvEngagement.activeSubtab || 'paliers';\n",
    'render fallback -> paliers')

# 3) Drop the 'focus' tab button from the sub-tab bar.
src = go(src,
    "      ${tabBtn('focus', engT('eng_subtab_focus'))}\n"
    "      ${tabBtn('paliers', engT('eng_subtab_paliers'))}\n"
    "      ${tabBtn('scoreboard', engT('eng_subtab_score'))}\n",
    "      ${tabBtn('paliers', engT('eng_subtab_paliers'))}\n"
    "      ${tabBtn('scoreboard', engT('eng_subtab_score'))}\n",
    'remove focus sub-tab button')

# 4) Remove the focus dispatch line — fall through to paliers.
src = go(src,
    "  if (sub === 'focus') gmvRenderEngagementFocus(panel, mySeller, isCreator);\n"
    "  else if (sub === 'paliers') gmvRenderEngagementPaliers(panel, mySeller, isCreator);\n"
    "  else gmvRenderEngagementScoreboard(panel, mySeller, isCreator);\n",
    "  if (sub === 'scoreboard') gmvRenderEngagementScoreboard(panel, mySeller, isCreator);\n"
    "  else gmvRenderEngagementPaliers(panel, mySeller, isCreator);\n",
    'dispatch: drop focus branch, default to paliers')

# 5) Defensive: if any older state has 'focus' saved, normalise on render entry.
src = go(src,
    "  const isCreator = (typeof gmvIsCreator === 'function') && gmvIsCreator();\n"
    "  const mySeller = (typeof gmvSellerName === 'function') ? gmvSellerName() : '';\n"
    "  const sub = gmvEngagement.activeSubtab || 'paliers';\n",
    "  const isCreator = (typeof gmvIsCreator === 'function') && gmvIsCreator();\n"
    "  const mySeller = (typeof gmvSellerName === 'function') ? gmvSellerName() : '';\n"
    "  if (gmvEngagement.activeSubtab === 'focus') gmvEngagement.activeSubtab = 'paliers';\n"
    "  const sub = gmvEngagement.activeSubtab || 'paliers';\n",
    'normalise legacy focus -> paliers')

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
