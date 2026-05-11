import io, sys
P = '/sessions/vibrant-tender-mayer/mnt/Rehab app ( planner) - Copie/rigab_app/index.html'
src = io.open(P, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
fails = []

def go(s, old, new, label):
    o = old.replace('\n', nl); n = new.replace('\n', nl)
    if n in s and o not in s: print('  [skip] ' + label); return s
    if o not in s: print('  [FAIL] ' + label); return s
    print('  [ok]   ' + label)
    return s.replace(o, n, 1)

def gomany(s, old, new, label):
    """Replace ALL occurrences when the same line appears in multiple
    parallel functions (gmvSelectedGmv vs gmvComputeSoldForSellerClient,
    etc.). Counts must match an expected number."""
    o = old.replace('\n', nl); n = new.replace('\n', nl)
    if n in s and o not in s:
        print('  [skip] ' + label); return s
    cnt = s.count(o)
    if cnt == 0:
        print('  [FAIL] ' + label); return s
    print('  [ok]   ' + label + ' (x' + str(cnt) + ')')
    return s.replace(o, n)


# ---- 1) qty -> gmv comparisons, in all 4 helpers + 1 inline check ------
src = gomany(src,
    "    if (meta.min && s.qty >= meta.min) achieved++;\n",
    "    if (meta.min && s.gmv >= meta.min) achieved++;\n",
    'helper achievement (s.qty -> s.gmv)')

src = gomany(src,
    "    if (meta.min && q >= meta.min) achieved++;\n",
    "    if (meta.min && g >= meta.min) achieved++;\n",
    'helper achievement Both (q -> g)')

# Update gmvClientAchievedBoth (per-client) similarly
src = go(src,
    "function gmvClientAchievedBoth(seller, phone, codes) {\n"
    "  const m1 = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M1);\n"
    "  const m2 = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M2);\n"
    "  let achieved = 0;\n"
    "  (codes || []).forEach(code => {\n"
    "    const meta = gmvEngagement.focusProducts[code] || {};\n"
    "    const q = ((m1[code] && m1[code].qty) || 0) + ((m2[code] && m2[code].qty) || 0);\n"
    "    if (meta.min && g >= meta.min) achieved++;\n"
    "  });\n"
    "  return achieved;\n"
    "}\n",
    "function gmvClientAchievedBoth(seller, phone, codes) {\n"
    "  const m1 = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M1);\n"
    "  const m2 = gmvComputeSoldForSellerClient(seller, phone, ENG_PERIOD_M2);\n"
    "  let achieved = 0;\n"
    "  (codes || []).forEach(code => {\n"
    "    const meta = gmvEngagement.focusProducts[code] || {};\n"
    "    const g = ((m1[code] && m1[code].gmv) || 0) + ((m2[code] && m2[code].gmv) || 0);\n"
    "    if (meta.min && g >= meta.min) achieved++;\n"
    "  });\n"
    "  return achieved;\n"
    "}\n",
    'gmvClientAchievedBoth: drop unused q variable')


# ---- 2) Inline expanded-list row: switch hit/pct/display to MAD --------
src = go(src,
    "                const qty = ((sM1[code] && sM1[code].qty) || 0) + ((sM2[code] && sM2[code].qty) || 0);\n"
    "                const mad = ((sM1[code] && sM1[code].gmv) || 0) + ((sM2[code] && sM2[code].gmv) || 0);\n"
    "                const min = meta.min || 0;\n"
    "                const hit = min > 0 && qty >= min;\n"
    "                const pct = min > 0 ? Math.min(100, Math.round((qty / min) * 100)) : (qty > 0 ? 100 : 0);\n",
    "                const qty = ((sM1[code] && sM1[code].qty) || 0) + ((sM2[code] && sM2[code].qty) || 0);\n"
    "                const mad = ((sM1[code] && sM1[code].gmv) || 0) + ((sM2[code] && sM2[code].gmv) || 0);\n"
    "                const min = meta.min || 0;\n"
    "                const hit = min > 0 && mad >= min;\n"
    "                const pct = min > 0 ? Math.min(100, Math.round((mad / min) * 100)) : (mad > 0 ? 100 : 0);\n",
    'expanded list: hit/pct now use MAD vs min')

# Replace the displayed delivered line: "Delivered: qty / min units · X MAD"
# becomes "Delivered: X MAD / min MAD · qty units"
src = go(src,
    "                    <div style=\"display:flex; gap:10px; flex-wrap:wrap; font-size:11px; color:#64748b; margin-top:3px;\">\n"
    "                      <span>${engT('pal_delivered')}: <b style=\"color:${hit ? '#16a34a' : '#0f172a'};\">${qty}</b>${min > 0 ? ' / ' + min : ''} ${engT('pal_units')}</span>\n"
    "                      <span>${fmt(mad)} MAD</span>\n"
    "                    </div>\n",
    "                    <div style=\"display:flex; gap:10px; flex-wrap:wrap; font-size:11px; color:#64748b; margin-top:3px;\">\n"
    "                      <span>${engT('pal_delivered')} : <b style=\"color:${hit ? '#16a34a' : '#0f172a'};\">${fmt(mad)}</b>${min > 0 ? ' / ' + fmt(min) : ''} MAD</span>\n"
    "                      ${qty > 0 ? `<span>${qty} ${engT('pal_units')}</span>` : ''}\n"
    "                    </div>\n",
    'expanded list: show delivered MAD vs min MAD (qty as secondary)')


# ---- 3) Compact the per-client card padding/fonts ----------------------
src = go(src,
    "      <div class=\"pal-card\" style=\"background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:14px; margin-bottom:12px;\">\n"
    "        <div style=\"display:flex; justify-content:space-between; align-items:flex-start; gap:8px; flex-wrap:wrap;\">\n"
    "          <div style=\"min-width:0; flex:1;\">\n"
    "            <div style=\"font-weight:700; font-size:15px; color:#0f172a; line-height:1.2;\">${gmvEscapeHtmlEng(cl.name || '(no name)')}</div>\n"
    "            <div style=\"font-family:monospace; font-size:11px; color:#94a3b8; margin-top:2px;\">${gmvEscapeHtmlEng(phone)}</div>\n"
    "          </div>\n"
    "          ${ach ? `<span style=\"background:#dbeafe; color:#1e40af; padding:3px 10px; border-radius:99px; font-size:11px; font-weight:600; white-space:nowrap;\">${engT('pal_achieved')} ${ach.palier}</span>` : ''}\n"
    "        </div>\n",
    "      <div class=\"pal-card\" style=\"background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; margin-bottom:8px;\">\n"
    "        <div style=\"display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap;\">\n"
    "          <div style=\"min-width:0; flex:1;\">\n"
    "            <div style=\"font-weight:700; font-size:13.5px; color:#0f172a; line-height:1.2; overflow:hidden; text-overflow:ellipsis;\">${gmvEscapeHtmlEng(cl.name || '(no name)')}</div>\n"
    "            <div style=\"font-family:monospace; font-size:10.5px; color:#94a3b8; margin-top:1px;\">${gmvEscapeHtmlEng(phone)}</div>\n"
    "          </div>\n"
    "          ${ach ? `<span style=\"background:#dbeafe; color:#1e40af; padding:2px 8px; border-radius:99px; font-size:10px; font-weight:700; white-space:nowrap;\">${engT('pal_achieved')} ${ach.palier}</span>` : ''}\n"
    "        </div>\n",
    'compact card header')

# Compact the "next target" / "all done" block
src = go(src,
    "          if (allDone) {\n"
    "            return `<div style=\"margin-top:12px; padding:10px 12px; border-radius:8px; background:#f0fdf4; border:1px solid #86efac; font-size:12px; color:#15803d; font-weight:600; text-align:center;\">${engT('pal_all_done')}</div>`;\n"
    "          }\n"
    "          if (!targetP) return '';\n"
    "          const remaining = Math.max(0, (targetP.threshold || 0) - cBoth);\n"
    "          const progPct = Math.min(100, Math.round((cBoth / (targetP.threshold || 1)) * 100));\n"
    "          return `<div style=\"margin-top:12px; padding-top:10px; border-top:1px solid #f1f5f9;\">\n"
    "            <div style=\"display:flex; justify-content:space-between; align-items:baseline; font-size:12px; gap:8px; flex-wrap:wrap;\">\n"
    "              <span style=\"color:#64748b;\">${engT('pal_next_target')} : <b style=\"color:#0f172a;\">${engT('pal_lvl', { n: targetP.palier })}</b></span>\n"
    "              <span style=\"color:#64748b; font-size:11px;\"><b style=\"color:#0f172a;\">${fmt(cBoth)}</b> / ${fmt(targetP.threshold)} MAD</span>\n"
    "            </div>\n"
    "            <div style=\"height:5px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:6px;\">\n"
    "              <div style=\"height:100%; width:${progPct}%; background:#3b82f6; transition:width .4s;\"></div>\n"
    "            </div>\n"
    "            <div style=\"font-size:11px; color:#64748b; margin-top:5px;\">${engT('pal_remaining', { n: fmt(remaining) })}</div>\n"
    "          </div>`;\n"
    "        })()}\n",
    "          if (allDone) {\n"
    "            return `<div style=\"margin-top:8px; padding:6px 10px; border-radius:6px; background:#f0fdf4; border:1px solid #86efac; font-size:11.5px; color:#15803d; font-weight:600; text-align:center;\">${engT('pal_all_done')}</div>`;\n"
    "          }\n"
    "          if (!targetP) return '';\n"
    "          const remaining = Math.max(0, (targetP.threshold || 0) - cBoth);\n"
    "          const progPct = Math.min(100, Math.round((cBoth / (targetP.threshold || 1)) * 100));\n"
    "          return `<div style=\"margin-top:8px; padding-top:8px; border-top:1px solid #f1f5f9;\">\n"
    "            <div style=\"display:flex; justify-content:space-between; align-items:baseline; font-size:11.5px; gap:8px; flex-wrap:wrap;\">\n"
    "              <span style=\"color:#64748b;\">${engT('pal_next_target')} : <b style=\"color:#0f172a;\">${engT('pal_lvl', { n: targetP.palier })}</b></span>\n"
    "              <span style=\"color:#64748b; font-size:10.5px;\"><b style=\"color:#0f172a;\">${fmt(cBoth)}</b> / ${fmt(targetP.threshold)} MAD</span>\n"
    "            </div>\n"
    "            <div style=\"height:3px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:5px;\">\n"
    "              <div style=\"height:100%; width:${progPct}%; background:#3b82f6; transition:width .4s;\"></div>\n"
    "            </div>\n"
    "            <div style=\"font-size:10.5px; color:#64748b; margin-top:3px;\">${engT('pal_remaining', { n: fmt(remaining) })}</div>\n"
    "          </div>`;\n"
    "        })()}\n",
    'compact next-target block')

# Compact the "my products" row
src = go(src,
    "        <div style=\"margin-top:10px; padding-top:10px; border-top:1px solid #f1f5f9;\">\n"
    "          <div style=\"display:flex; justify-content:space-between; align-items:center; font-size:12px;\">\n"
    "            <span style=\"color:#64748b;\">${engT('pal_my_products')} : <b style=\"color:${prodOk ? '#16a34a' : '#dc2626'};\">${myProds.length}</b><span style=\"color:#94a3b8;\"> / ${ENG_CLIENT_MIN_PRODUCTS}</span></span>\n"
    "            <button type=\"button\" data-pal-edit=\"${gmvEscapeHtmlEng(phone)}\" style=\"background:#0f172a; border:0; color:#fff; padding:5px 12px; border-radius:6px; font-size:11px; font-weight:600; cursor:pointer;\">${engT('pal_edit')}</button>\n"
    "          </div>\n"
    "          <div style=\"height:4px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:6px;\">\n"
    "            <div style=\"height:100%; width:${prodPct}%; background:${prodOk ? '#16a34a' : '#3b82f6'}; transition:width .4s;\"></div>\n"
    "          </div>\n",
    "        <div style=\"margin-top:8px; padding-top:8px; border-top:1px solid #f1f5f9;\">\n"
    "          <div style=\"display:flex; justify-content:space-between; align-items:center; font-size:11.5px; gap:8px;\">\n"
    "            <span style=\"color:#64748b;\">${engT('pal_my_products')} : <b style=\"color:${prodOk ? '#16a34a' : '#dc2626'};\">${myProds.length}</b><span style=\"color:#94a3b8;\"> / ${ENG_CLIENT_MIN_PRODUCTS}</span></span>\n"
    "            <button type=\"button\" data-pal-edit=\"${gmvEscapeHtmlEng(phone)}\" style=\"background:#0f172a; border:0; color:#fff; padding:4px 10px; border-radius:6px; font-size:10.5px; font-weight:600; cursor:pointer;\">${engT('pal_edit')}</button>\n"
    "          </div>\n"
    "          <div style=\"height:3px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:4px;\">\n"
    "            <div style=\"height:100%; width:${prodPct}%; background:${prodOk ? '#16a34a' : '#3b82f6'}; transition:width .4s;\"></div>\n"
    "          </div>\n",
    'compact my-products row')

# Compact the gift status rows
src = go(src,
    "    const giftRow = (label, count, total, pct, open, gmvCur, gmvTgt) => `\n"
    "      <div style=\"display:flex; justify-content:space-between; align-items:center; gap:10px; padding:10px 12px; background:${open ? '#f0fdf4' : '#f8fafc'}; border:1px solid ${open ? '#86efac' : '#e2e8f0'}; border-radius:8px; margin-top:8px;\">\n"
    "        <div style=\"flex:1; min-width:0;\">\n"
    "          <div style=\"display:flex; align-items:center; gap:6px; font-size:12.5px; font-weight:600; color:#0f172a;\">\n"
    "            <span>${label}</span>\n"
    "            <span style=\"font-size:11px; font-weight:600; color:${open ? '#16a34a' : '#94a3b8'};\">${open ? '🎁 ' + engT('pal_gift_open') : engT('pal_gift_locked')}</span>\n"
    "          </div>\n"
    "          <div style=\"display:flex; gap:10px; flex-wrap:wrap; font-size:11px; color:#64748b; margin-top:4px;\">\n"
    "            <span><b style=\"color:${count >= total ? '#16a34a' : '#0f172a'};\">${count}</b> / ${total} ${engT('pal_products')}</span>\n"
    "            ${gmvTgt ? `<span><b style=\"color:${gmvCur >= gmvTgt ? '#16a34a' : '#0f172a'};\">${fmt(gmvCur)}</b> / ${fmt(gmvTgt)} MAD</span>` : `<span style=\"color:#dc2626;\">${engT('pal_no_target_set')}</span>`}\n"
    "          </div>\n"
    "          <div style=\"height:4px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:6px;\">\n"
    "            <div style=\"height:100%; width:${pct}%; background:${open ? '#16a34a' : '#3b82f6'}; transition:width .4s;\"></div>\n"
    "          </div>\n"
    "        </div>\n"
    "      </div>`;\n",
    "    const giftRow = (label, count, total, pct, open, gmvCur, gmvTgt) => `\n"
    "      <div style=\"display:flex; justify-content:space-between; align-items:center; gap:8px; padding:6px 10px; background:${open ? '#f0fdf4' : '#f8fafc'}; border:1px solid ${open ? '#86efac' : '#e2e8f0'}; border-radius:6px; margin-top:6px;\">\n"
    "        <div style=\"flex:1; min-width:0;\">\n"
    "          <div style=\"display:flex; align-items:center; gap:6px; font-size:11.5px; font-weight:600; color:#0f172a; flex-wrap:wrap;\">\n"
    "            <span>${label}</span>\n"
    "            <span style=\"font-size:10.5px; font-weight:700; color:${open ? '#16a34a' : '#94a3b8'};\">${open ? '🎁 ' + engT('pal_gift_open') : engT('pal_gift_locked')}</span>\n"
    "          </div>\n"
    "          <div style=\"display:flex; gap:8px; flex-wrap:wrap; font-size:10.5px; color:#64748b; margin-top:2px;\">\n"
    "            <span><b style=\"color:${count >= total ? '#16a34a' : '#0f172a'};\">${count}</b>/${total} ${engT('pal_products')}</span>\n"
    "            ${gmvTgt ? `<span><b style=\"color:${gmvCur >= gmvTgt ? '#16a34a' : '#0f172a'};\">${fmt(gmvCur)}</b>/${fmt(gmvTgt)} MAD</span>` : `<span style=\"color:#dc2626;\">${engT('pal_no_target_set')}</span>`}\n"
    "          </div>\n"
    "          <div style=\"height:2px; background:#f1f5f9; border-radius:99px; overflow:hidden; margin-top:4px;\">\n"
    "            <div style=\"height:100%; width:${pct}%; background:${open ? '#16a34a' : '#3b82f6'}; transition:width .4s;\"></div>\n"
    "          </div>\n"
    "        </div>\n"
    "      </div>`;\n",
    'compact gift status rows')


if fails:
    print('FAIL — not writing. ' + str(len(fails)) + ' step(s) failed.')
    sys.exit(2)

io.open(P, 'w', encoding='utf-8', newline='').write(src)
print('Done.')
