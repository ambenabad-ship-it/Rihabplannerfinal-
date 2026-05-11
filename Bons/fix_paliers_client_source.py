# -*- coding: utf-8 -*-
"""
Paliers tab — sellers should see all clients assigned to them, whether
the assignment came from the uploaded clients file (gmv.clients[phone].seller)
or from a manual claim in the client pool (gmvClientAssignments.byPhone).

Previously only manual claims were considered, so sellers without claims
saw an empty page even when their clients existed in the uploaded file.
"""
import io, os, sys

INDEX_PATH = '/sessions/vibrant-tender-mayer/mnt/Rehab app ( planner) - Copie/rigab_app/index.html'
src = io.open(INDEX_PATH, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'

OLD = (
    "  // Sorted, claimed client phones for this seller.\n"
    "  const myPhones = [];\n"
    "  Object.entries(gmvClientAssignments.byPhone || {}).forEach(([phone, a]) => {\n"
    "    if (a.seller === seller) myPhones.push(phone);\n"
    "  });\n"
).replace('\n', nl)

NEW = (
    "  // Build the seller's client list from BOTH sources:\n"
    "  //   1. Manual claim   -> gmvClientAssignments.byPhone[phone].seller\n"
    "  //   2. Clients file   -> gmv.clients[phone].seller\n"
    "  // Manual claim wins (matches gmvComputeSoldForSeller's logic).\n"
    "  const myPhones = [];\n"
    "  const _seenPhones = new Set();\n"
    "  Object.entries(gmv.clients || {}).forEach(([phone, c]) => {\n"
    "    const claim = gmvClientAssignments && gmvClientAssignments.byPhone\n"
    "      ? gmvClientAssignments.byPhone[phone]\n"
    "      : null;\n"
    "    const assigned = (claim && claim.seller) || (c && c.seller) || '';\n"
    "    if (assigned === seller && !_seenPhones.has(phone)) {\n"
    "      _seenPhones.add(phone);\n"
    "      myPhones.push(phone);\n"
    "    }\n"
    "  });\n"
    "  // Also include any phones that are claimed but were missing from\n"
    "  // gmv.clients (defensive — keeps the manual claim flow working).\n"
    "  Object.entries(gmvClientAssignments.byPhone || {}).forEach(([phone, a]) => {\n"
    "    if (a.seller === seller && !_seenPhones.has(phone)) {\n"
    "      _seenPhones.add(phone);\n"
    "      myPhones.push(phone);\n"
    "    }\n"
    "  });\n"
).replace('\n', nl)

if NEW in src and OLD not in src:
    print('  [skip] already applied')
elif OLD not in src:
    print('  [FAIL] anchor not found')
    sys.exit(2)
else:
    src = src.replace(OLD, NEW, 1)
    io.open(INDEX_PATH, 'w', encoding='utf-8', newline='').write(src)
    print('  [ok]   paliers tab now reads clients from upload + manual claims')
