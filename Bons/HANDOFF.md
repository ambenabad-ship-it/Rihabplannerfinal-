# GMV Tracker — Session Handoff

## Repo
- File: `C:\Users\KamalSAGUEM\OneDrive - Beyond believers\Bureau\Rehab app ( planner) - Copie\rigab_app\index.html` (~18,500 lines)
- Git: `https://github.com/ambenabad-ship-it/Rihabplannerfinal-` — work on `better` branch
- Push: `git push origin better` (NOT `better:main` — that goes to wrong branch)

## CRITICAL session constraint
The `- Copie\rigab_app` folder is **read-only via Edit/Write tools** in Claude sessions, and the Linux sandbox often refuses to start. Workaround: write Python patch scripts to `…\Rehab app ( planner)\Bons\` and have the user run them in PowerShell. Each patch must be:
- Idempotent (`if marker in src: skip`)
- Use unique anchors (the file has `if (scope === 'client-store') {` 3x — must include surrounding lines)
- Watch out for `×` (×) and `·` (·) — file uses literal escapes in JS strings, must match in Python

## What this session shipped (in order)

1. **Product Categories upload** — 3rd tile in GMV Tracker (Code/Description/Category), captures `partnerCode` per order as `productCode`, persists to localStorage (`rihab_gmv_categories_v1`) + Supabase (`gmv_categories`). Renders "GMV by Category" on Performance.
2. **Category + Store×Category targets** — new scopes in flat Targets view. Store target shared between Seller branch and Category branch. Caps via `gmvBudgetCapMulti`. Category cap is OPTIONAL (only applies if set).
3. **Store × Category rows** filtered to pairs that exist in orders (not cartesian).
4. **Performance page redesign** — replaced 3-tab "By Seller/Store/Category" with multi-dim group-by chips (Seller / Store / Client / Category). Dynamic columns. Filter chips for sellers/stores/clients/categories. Search. State persisted to localStorage.
5. **Bullet chart redesign** — target = right edge of bar (no more 75% tick mark). Fill turns green when ≥ target. Applied to: hero bullet, inline `bullet()` helper, byStore rows, byStore grand total, flat performance.
6. **Hero bullet labels** — "0" left, "target {amount}" right (was overlapping before).
7. **Roles Phase 1** — `GMV_CREATOR_EMAIL = 'ahmed.mouatamid@z.systems'`. Non-creators get viewer mode: upload tiles hidden via JS + CSS body class `gmv-is-viewer`, blue banner explains.
8. **Roles Phase 2 (in code, NOT activated)** — `gmvReadShared(key)` reads from creator's user_data row when `GMV_CREATOR_USER_ID` is set. Currently empty — needs creator UUID + Supabase RLS policy.

## State of features

### Working
- Categories upload + Performance by Category
- Category targets, Store×Category targets with linked caps
- Performance page multi-dim group-by + filters
- Bullet chart with target = right edge
- Phase 1 role lock-down (UI hidden for non-creators)

### Pending (Phase 2 last mile)
The user uploaded files from creator account but viewers don't see the data. To finish:

1. Creator signs in → yellow banner shows their UUID at top of GMV Tracker
2. Paste UUID into `const GMV_CREATOR_USER_ID = '';` in `index.html`
3. Run this SQL in Supabase → SQL Editor (with UUID substituted):
   ```sql
   DROP POLICY IF EXISTS "viewers read creator gmv" ON user_data;
   CREATE POLICY "viewers read creator gmv"
   ON user_data FOR SELECT
   TO authenticated
   USING (
     user_id = '<UUID>'::uuid
     AND key IN ('gmv_clients', 'gmv_orders', 'gmv_names', 'gmv_categories')
   );
   ```
4. Push to git, viewers hard-refresh.

## Key state shape

```js
const gmv = {
  clients: {},              // phone -> {name, seller, retailerId}
  orders: [],               // [{phone, date, amount, status, store, productCode}]
  productCategories: {},    // code -> {description, category}
  namesByPhone: {},
  dateFrom: '', dateTo: '',
  targets: {},              // periodKey -> {sellers, clients, stores, storesBySeller,
                            //               storesByClient, categories, categoriesByStore, global}
  // ... lots of UI state ...
  perfDims: ['seller'],     // multi-select group-by
  perfFilters: { sellers, stores, clients, categories, search },
  perfLimit: 50,
};
```

## Localstorage keys
`rihab_gmv_targets_v1, _range_v1, _clients_v1, _orders_v1, _names_v1, _categories_v1, _page_v1, _tview_v1, _perfdims_v1, _perfscope_v1, _perfview_v1`

## Supabase keys (in `user_data` table, JSONB value)
`gmv_clients, gmv_orders, gmv_names, gmv_targets, gmv_range, gmv_categories, planning_history`

## Important helpers
- `gmvBudgetCap(parent, siblingsSumIncludingSelf, ownValue)` — single-parent cap with room-left HTML
- `gmvBudgetCapMulti([{parent, siblingsSumIncludingSelf, label}, ...], ownValue)` — tightest of N
- `gmvActivePeriodBucket()` — returns the period-keyed targets object, lazy-creates with all required fields
- `gmvIsCreator()` — returns `sbUser.email === GMV_CREATOR_EMAIL`
- `gmvDataSourceUserId()` — returns own UUID for creator, `GMV_CREATOR_USER_ID` for viewers
- `gmvReadShared(key)` — `sbReadKeyAs(gmvDataSourceUserId(), key)`

## Recent patch scripts (in `Bons/`)
- `apply_categories_patch.py` — initial categories upload feature
- `apply_categories_tile_fix.py` — fixed missed UI tile insertion
- `apply_category_targets.py` through `_v6.py` — iterations on category targets caps + UI
- `apply_category_caps_fix.py` — added missing caps that v3 dropped on crash
- `fix_storecat_optional_cat.py` — made category target optional in store×category
- `apply_perf_tabs.py` — initial 3-tab perf view (superseded)
- `apply_perf_flat_view.py` — flat scope-based perf view (superseded)
- `apply_perf_dims.py` — multi-dim group-by (current)
- `fix_bullet_labels.py`, `_v2.py`, `fix_bullet_no_tick.py` — bullet redesign
- `apply_role_lockdown.py` — phase 1
- `apply_role_shared_reads.py` — phase 2 JS (waiting on UUID + SQL)
- `fix_role_apply_on_signin.py` — role check on auth state change
- `fix_role_css_class.py` — body class belt-and-braces

## Next concrete action
Walk user through getting the creator UUID from their browser console (or the yellow banner) and run the SQL with it. Then verify viewer can see creator's clients/orders/categories.
