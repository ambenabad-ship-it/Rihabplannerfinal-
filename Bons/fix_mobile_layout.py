# -*- coding: utf-8 -*-
"""
Mobile layout fixes — comprehensive pass.

Addresses the audit findings on http://zcontroltower.com/rigab_app/index.html
viewed at 388x552:

  Bug 2  Hamburger overlaps content (no top safe-area on app panes for the
         settings + GMV + ff feature panes which override .app's padding).
  Bug 3  Fixed bottom auth chip overflows the viewport on narrow screens
         and covers the last row of every page.
  Bug 4  Step chips ('Clients/Schedule/Orders/Stock/Process') overflow
         horizontally with no scroll affordance.
  Bug 5  Order Fulfillment table scroll has no visible scrollbar.
  Bug 7  Planner page-nav buttons wrap awkwardly (Bons drops to row 2).
  Bug 8  GMV Tracker top is clipped under the hamburger on mobile.
  Bug 9  Settings heading sits flush against the hamburger.
  Bug 10 The page does not scroll past inner feature container.
  Bug 13 Hamburger lacks safe-area-inset-top/-left for iOS notches.

Bug 1 (Planner/Settings hidden in sidebar) is INTENDED behaviour: those two
features are seller-locked. Sellers see only Order Fulfillment + GMV Tracker
by design (gmvIsSeller() in JS). Skipped.

Bug 6 (#awalRenderHost is 794px wide) is a false positive. The element is
position:absolute; left:-10000px — it is rendered off-screen by design for
the html2pdf pipeline and does not affect document flow on mobile.

Run from PowerShell:
  python fix_mobile_layout.py

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
    print('Could not find index.html. Tried:')
    for c in candidates:
        print('  ' + c)
    sys.exit(1)


INDEX_PATH = _find_index()
MARKER_BEGIN = '/* === MOBILE LAYOUT FIXES — fix_mobile_layout.py === */'
MARKER_END   = '/* === END MOBILE LAYOUT FIXES === */'


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


# All the new mobile rules go in one block we can re-inject. Putting them
# at the very end of the existing global <style> means they win against
# the per-feature mobile blocks already in the file (which clobber the
# .app padding-top rule from line 221).
MOBILE_BLOCK = (
    MARKER_BEGIN + '\n'
    '  /* Bug 13 — Safe-area for hamburger toggle (iOS notch). */\n'
    '  .as-toggle {\n'
    '    top: calc(env(safe-area-inset-top, 0px) + 12px) !important;\n'
    '    left: calc(env(safe-area-inset-left, 0px) + 12px) !important;\n'
    '  }\n'
    '\n'
    '  @media (max-width: 900px) {\n'
    '    /* Bug 2/8/9 — every feature pane needs space below the fixed\n'
    '       hamburger. The per-feature mobile blocks below override the\n'
    '       earlier .app padding-top rule, so we re-apply it here with\n'
    '       higher specificity. */\n'
    '    .app-main > .app,\n'
    '    .app-main > .ff-app,\n'
    '    .app-main > .gmv-app,\n'
    '    .app-main > .settings-app,\n'
    '    .app-main > #featurePlanner {\n'
    '      padding-top: 64px !important;\n'
    '      padding-bottom: 88px !important;\n'
    '    }\n'
    '\n'
    '    /* Bug 10 — let the document scroll, not an inner pane. */\n'
    '    html, body { height: auto !important; min-height: 100%; overflow-x: hidden; }\n'
    '    .app-shell { min-height: 100vh; height: auto; align-items: stretch; }\n'
    '    .app-sidebar { /* sticky on desktop, fixed on mobile already */ }\n'
    '\n'
    '    /* Bug 3 — auth chip must stay inside the viewport and not eat\n'
    '       the bottom row of content. */\n'
    '    .sb-auth-chip {\n'
    '      left: 8px !important; right: 8px !important;\n'
    '      bottom: calc(env(safe-area-inset-bottom, 0px) + 8px) !important;\n'
    '      max-width: calc(100vw - 16px);\n'
    '      flex-wrap: wrap; justify-content: center;\n'
    '    }\n'
    '    .sb-auth-chip .sb-auth-email { max-width: calc(100vw - 140px); }\n'
    '\n'
    '    /* Bug 4 — stepper: scrollable + visible scrollbar so users see\n'
    '       there is more content to the side. */\n'
    '    .stepper {\n'
    '      flex-wrap: nowrap;\n'
    '      -webkit-overflow-scrolling: touch;\n'
    '      scrollbar-width: thin;\n'
    '      scroll-snap-type: x proximity;\n'
    '      padding-bottom: 4px;\n'
    '    }\n'
    '    .stepper::-webkit-scrollbar { height: 4px; }\n'
    '    .stepper::-webkit-scrollbar-thumb { background: rgba(15,23,42,.18); border-radius: 99px; }\n'
    '    .stepper .step-chip { scroll-snap-align: start; flex-shrink: 0; }\n'
    '\n'
    '    /* Bug 5 — Order Fulfillment table scrollers always show their\n'
    '       scrollbar so users discover the right-hand columns. */\n'
    '    .ff-table-wrap, .ff-tabs {\n'
    '      scrollbar-width: thin;\n'
    '    }\n'
    '    .ff-table-wrap::-webkit-scrollbar,\n'
    '    .ff-tabs::-webkit-scrollbar { height: 6px; }\n'
    '    .ff-table-wrap::-webkit-scrollbar-thumb,\n'
    '    .ff-tabs::-webkit-scrollbar-thumb { background: rgba(15,23,42,.22); border-radius: 99px; }\n'
    '    /* Fade affordance on the right edge of horizontally scrollable\n'
    '       wrappers so the cut-off content is obvious. */\n'
    '    .ff-table-wrap, .stepper, .ff-tabs, .gmv-pagebar {\n'
    '      background-image: linear-gradient(to right, transparent calc(100% - 24px), rgba(15,23,42,.06));\n'
    '      background-position: right top;\n'
    '      background-size: 24px 100%;\n'
    '      background-repeat: no-repeat;\n'
    '    }\n'
    '\n'
    '    /* Bug 7 — Planner page-nav: scrollable pill bar instead of wrap. */\n'
    '    .page-nav {\n'
    '      flex-wrap: nowrap !important;\n'
    '      overflow-x: auto;\n'
    '      -webkit-overflow-scrolling: touch;\n'
    '      scrollbar-width: thin;\n'
    '      padding-bottom: 4px;\n'
    '    }\n'
    '    .page-nav::-webkit-scrollbar { height: 4px; }\n'
    '    .page-nav::-webkit-scrollbar-thumb { background: rgba(15,23,42,.18); border-radius: 99px; }\n'
    '    .page-nav-btn { flex: 0 0 auto !important; white-space: nowrap; }\n'
    '  }\n'
    + MARKER_END
)


def main():
    print('Patching: ' + INDEX_PATH)
    src = read_file(INDEX_PATH)

    # Strip any previous version of the block so we can re-inject cleanly.
    if MARKER_BEGIN in src and MARKER_END in src:
        a = src.index(MARKER_BEGIN)
        b = src.index(MARKER_END) + len(MARKER_END)
        # Trim trailing newline(s) and any leading 2-space indent we
        # injected before the marker, so we can re-inject without
        # piling up whitespace.
        end = b
        while end < len(src) and src[end] in ('\n', '\r'):
            end += 1
        start = a
        # Strip the "  " indent we wrote in front of the begin marker.
        if start >= 2 and src[start-2:start] == '  ':
            start -= 2
        # Strip the leading newline that preceded the indent.
        while start > 0 and src[start-1] in ('\n', '\r'):
            start -= 1
        src = src[:start] + src[end:]
        print('  [ok]   removed previous mobile block (re-applying)')

    # Detect newline style so the new block matches the surrounding file.
    nl = '\r\n' if '\r\n' in src else '\n'

    # Inject just before the </style> that closes the main global stylesheet.
    # That </style> is the one immediately before <div class="app ff-app">.
    anchor = nl + '  /* RTL fine-tuning for Arabic */' + nl
    if anchor not in src:
        print('  [FAIL] could not find anchor for global mobile block')
        sys.exit(2)
    if src.count(anchor) != 1:
        print('  [FAIL] anchor not unique')
        sys.exit(2)
    block = MOBILE_BLOCK.replace('\n', nl)
    src = src.replace(anchor, nl + '  ' + block + nl + anchor, 1)
    print('  [ok]   injected mobile fixes block')

    write_file(INDEX_PATH, src)
    print('Done.')


if __name__ == '__main__':
    main()
