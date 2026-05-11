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

# 1) Upload bar reads a transient flag and flips colors when "uploaded".
src = go(src,
    "  const uploadsHtml = isCreator ? `\n"
    "    <div style=\"display:flex; gap:10px; flex-wrap:wrap; margin:0 0 14px; padding:10px 12px; background:#fef3c7; border:1px solid #fde68a; border-radius:8px;\">\n"
    "      <span style=\"font-size:12px; color:#92400e; align-self:center;\"><b>Creator setup:</b></span>\n"
    "      <label class=\"btn\" style=\"font-size:12px; cursor:pointer;\">Upload focus products\n"
    "        <input type=\"file\" id=\"engFocusUpload\" accept=\".xlsx,.xls,.csv\" style=\"display:none;\">\n"
    "      </label>\n"
    "      <label class=\"btn\" style=\"font-size:12px; cursor:pointer;\">Upload paliers\n"
    "        <input type=\"file\" id=\"engPaliersUpload\" accept=\".xlsx,.xls,.csv\" style=\"display:none;\">\n"
    "      </label>\n"
    "      <span style=\"font-size:11px; color:#78350f; align-self:center;\">\n"
    "        ${Object.keys(gmvEngagement.focusProducts).length} SKU(s) · ${gmvEngagement.paliers.length} palier(s)\n"
    "      </span>\n"
    "    </div>` : '';\n",
    "  // Show a green 'saved' state on the upload bar right after a successful\n"
    "  // upload. The flag is cleared after a short delay.\n"
    "  const _uploadOk = !!gmvEngagement._uploadJustOk;\n"
    "  const _uploadStyle = _uploadOk\n"
    "    ? 'background:#dcfce7; border:1px solid #86efac;'\n"
    "    : 'background:#fef3c7; border:1px solid #fde68a;';\n"
    "  const _uploadLabelCol = _uploadOk ? '#14532d' : '#92400e';\n"
    "  const _uploadCountCol = _uploadOk ? '#166534' : '#78350f';\n"
    "  const _uploadLabel = _uploadOk ? '✓ Saved — ' : 'Creator setup:';\n"
    "  const uploadsHtml = isCreator ? `\n"
    "    <div style=\"display:flex; gap:10px; flex-wrap:wrap; margin:0 0 14px; padding:10px 12px; ${_uploadStyle} border-radius:8px; transition: background .3s, border-color .3s;\">\n"
    "      <span style=\"font-size:12px; color:${_uploadLabelCol}; align-self:center;\"><b>${_uploadLabel}</b></span>\n"
    "      <label class=\"btn\" style=\"font-size:12px; cursor:pointer;\">Upload focus products\n"
    "        <input type=\"file\" id=\"engFocusUpload\" accept=\".xlsx,.xls,.csv\" style=\"display:none;\">\n"
    "      </label>\n"
    "      <label class=\"btn\" style=\"font-size:12px; cursor:pointer;\">Upload paliers\n"
    "        <input type=\"file\" id=\"engPaliersUpload\" accept=\".xlsx,.xls,.csv\" style=\"display:none;\">\n"
    "      </label>\n"
    "      <span style=\"font-size:11px; color:${_uploadCountCol}; align-self:center;\">\n"
    "        ${Object.keys(gmvEngagement.focusProducts).length} SKU(s) · ${gmvEngagement.paliers.length} palier(s)\n"
    "      </span>\n"
    "    </div>` : '';\n",
    'upload bar reads _uploadJustOk and flips green')

# 2) On successful upload, flip the flag for 2.5 s then clear it.
src = go(src,
    "  const fU = document.getElementById('engFocusUpload');\n"
    "  if (fU) fU.addEventListener('change', async e => {\n"
    "    const f = e.target.files && e.target.files[0]; if (!f) return;\n"
    "    try { await gmvOnUploadFocus(f); gmvRenderEngagement(wrap); }\n"
    "    catch (err) { alert('Focus upload error: ' + (err.message || err)); }\n"
    "    try { e.target.value = ''; } catch (_) {}\n"
    "  });\n"
    "  const pU = document.getElementById('engPaliersUpload');\n"
    "  if (pU) pU.addEventListener('change', async e => {\n"
    "    const f = e.target.files && e.target.files[0]; if (!f) return;\n"
    "    try { await gmvOnUploadPaliers(f); gmvRenderEngagement(wrap); }\n"
    "    catch (err) { alert('Paliers upload error: ' + (err.message || err)); }\n"
    "    try { e.target.value = ''; } catch (_) {}\n"
    "  });\n",
    "  const _flashOk = () => {\n"
    "    gmvEngagement._uploadJustOk = true;\n"
    "    gmvRenderEngagement(wrap);\n"
    "    clearTimeout(gmvEngagement._uploadFlashT);\n"
    "    gmvEngagement._uploadFlashT = setTimeout(() => {\n"
    "      gmvEngagement._uploadJustOk = false;\n"
    "      try { gmvRenderEngagement(wrap); } catch (_) {}\n"
    "    }, 2500);\n"
    "  };\n"
    "  const fU = document.getElementById('engFocusUpload');\n"
    "  if (fU) fU.addEventListener('change', async e => {\n"
    "    const f = e.target.files && e.target.files[0]; if (!f) return;\n"
    "    try { await gmvOnUploadFocus(f); _flashOk(); }\n"
    "    catch (err) { alert('Focus upload error: ' + (err.message || err)); }\n"
    "    try { e.target.value = ''; } catch (_) {}\n"
    "  });\n"
    "  const pU = document.getElementById('engPaliersUpload');\n"
    "  if (pU) pU.addEventListener('change', async e => {\n"
    "    const f = e.target.files && e.target.files[0]; if (!f) return;\n"
    "    try { await gmvOnUploadPaliers(f); _flashOk(); }\n"
    "    catch (err) { alert('Paliers upload error: ' + (err.message || err)); }\n"
    "    try { e.target.value = ''; } catch (_) {}\n"
    "  });\n",
    'success handler: flash green for 2.5s')

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
