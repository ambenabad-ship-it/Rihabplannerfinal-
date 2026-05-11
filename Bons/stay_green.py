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

# Make the bar green whenever BOTH datasets have data; yellow only when
# something is missing. The 2.5 s flash is gone.
src = go(src,
    "  // Show a green 'saved' state on the upload bar right after a successful\n"
    "  // upload. The flag is cleared after a short delay.\n"
    "  const _uploadOk = !!gmvEngagement._uploadJustOk;\n"
    "  const _uploadStyle = _uploadOk\n"
    "    ? 'background:#dcfce7; border:1px solid #86efac;'\n"
    "    : 'background:#fef3c7; border:1px solid #fde68a;';\n"
    "  const _uploadLabelCol = _uploadOk ? '#14532d' : '#92400e';\n"
    "  const _uploadCountCol = _uploadOk ? '#166534' : '#78350f';\n"
    "  const _uploadLabel = _uploadOk ? '✓ Saved — ' : 'Creator setup:';\n",
    "  // The bar is green whenever BOTH focus + paliers are loaded.\n"
    "  // Yellow means something is still missing.\n"
    "  const _focusN = Object.keys(gmvEngagement.focusProducts || {}).length;\n"
    "  const _palierN = (gmvEngagement.paliers || []).length;\n"
    "  const _uploadOk = _focusN > 0 && _palierN > 0;\n"
    "  const _uploadStyle = _uploadOk\n"
    "    ? 'background:#dcfce7; border:1px solid #86efac;'\n"
    "    : 'background:#fef3c7; border:1px solid #fde68a;';\n"
    "  const _uploadLabelCol = _uploadOk ? '#14532d' : '#92400e';\n"
    "  const _uploadCountCol = _uploadOk ? '#166534' : '#78350f';\n"
    "  const _uploadLabel = _uploadOk ? '✓ Loaded' : 'Creator setup:';\n",
    'bar color follows loaded-state, not transient flag')

# Drop the flash setTimeout — flag mechanism is no longer needed but the
# helper is still called; make it a no-op so we don't have to edit the
# call sites, and so the function isn't undefined.
src = go(src,
    "  const _flashOk = () => {\n"
    "    gmvEngagement._uploadJustOk = true;\n"
    "    gmvRenderEngagement(wrap);\n"
    "    clearTimeout(gmvEngagement._uploadFlashT);\n"
    "    gmvEngagement._uploadFlashT = setTimeout(() => {\n"
    "      gmvEngagement._uploadJustOk = false;\n"
    "      try { gmvRenderEngagement(wrap); } catch (_) {}\n"
    "    }, 2500);\n"
    "  };\n",
    "  // No transient flash anymore — re-rendering after a successful upload\n"
    "  // is enough; the bar will switch to green automatically because both\n"
    "  // counts will be > 0.\n"
    "  const _flashOk = () => { try { gmvRenderEngagement(wrap); } catch (_) {} };\n",
    'drop flash timer, _flashOk just re-renders')

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
