# Awal Delivery Documents — Browser App Feature Spec

**Goal:** Add a feature to my existing browser app that takes daily delivery files as input and produces two sets of PDFs as output: **Bons de Chargement** (loading sheets, one per delivery agent) and **Bons de Livraison / Invoices** (one PDF per agent containing one page per order).

This spec is the complete, self-contained handoff. Read it end-to-end before writing code. Reference Python implementations in `python_reference/` show the exact rendering logic that has been validated against real data.

---

## 1. User flow (what the feature does)

1. User opens the feature page in the browser app.
2. **First-time setup**: user uploads the product master catalog (`Export_Articles_Matjar.xlsx`). The app parses it and stores the result in IndexedDB. This step is one-time — subsequent visits read from cache. There is an "Update catalog" button to re-upload when products change.
3. **Per-delivery workflow**, user uploads three files for the day:
   - `dispatchers-YYYY-MM-DD.csv` — orders → delivery agents
   - `Confirmed_deliveries_YYYY-MM-DD.xlsx` — line-level products with quantity + status (Delivered / Partial / Out of stock)
   - **Optional**: a manual-patch JSON for orders missing from confirmed file (rare; needed when an order's data wasn't captured)
4. The app computes everything client-side, shows a summary preview (per agent: order count, deliverable total, anomalies).
5. User clicks **"Generate PDFs"**. The app produces:
   - `bons_chargement_YYYY-MM-DD.zip` — one PDF per agent (loading sheet)
   - `bons_livraison_YYYY-MM-DD.zip` — one PDF per agent containing per-order invoices
   - Or two single ZIPs containing both, plus individual download buttons per agent.

No backend. No data leaves the browser.

---

## 2. Tech stack & libraries

Framework-agnostic. Core logic lives in plain ES modules. The handful of dependencies:

| Purpose | Library | Why |
|---|---|---|
| Parse Excel | `xlsx` (SheetJS, MIT) | Robust XLSX parsing in browser |
| Parse CSV | `papaparse` | Stream-friendly, handles quoted fields |
| IndexedDB | `idb` (by Jake Archibald) | Tiny promise wrapper for IndexedDB |
| HTML → PDF | `html2pdf.js` (combines html2canvas + jsPDF) | Bulk-export many pages without user interaction. Renders Arabic RTL via the browser DOM, then rasterizes — Arabic shaping is correct. |
| ZIP bundle | `jszip` + `file-saver` | Pack all PDFs into one archive |

`html2pdf.js` is the right choice over pure `pdf-lib` because Arabic bidi/shaping in vector PDFs requires shipping a font + a shaping engine — heavyweight and fragile. Rasterized PDFs from the browser's own renderer match the validated Python output exactly.

If your existing app already uses one of these, reuse it. Otherwise add via your package manager.

---

## 3. Input file specifications

### 3.1 `Export_Articles_Matjar.xlsx` (master catalog — one-time upload)

- Single sheet named **`Products`** (~4200 rows)
- Columns we need:

| Column | Type | Used for |
|---|---|---|
| `Code` | string, e.g. `ART01975` | Primary key |
| `Description` | string (French) | Fallback display only |
| `Arabic description` | string (Arabic) | Primary display name |
| `Atomic barcode` | string/number | Per-unit barcode |
| `Package barcode` | string/number | Per-carton barcode |
| `Sell unit` | `'ATOMIC'` or `'PACKING'` | Determines which unit code to read |
| `Atomic unit` | int (1, 2, 5, 6, 7, 10) | Maps to Arabic unit name |
| `Packing unit` | int (2, 3, 5) | Maps to Arabic unit name |
| `Package quantity` | int | Multiplier in colisage string |

**Other columns exist** (`Category`, `Activated`, `Points`); ignore them for now.

**Stored in IndexedDB** as object store `articles` with key = `Code`, value = the row object.

### 3.2 `dispatchers-YYYY-MM-DD.csv`

```
Code,Status,Order date,Delivery date,Total price,Delivery agent,Order
CMD260416295,TO_DELIVER,17/04/2026 10:36:41,30/04/2026,27838.80,L119,1
```

- `Code` — order code, format `CMD\d{11}` or `CMD\d{8,12}` (codes can vary in length)
- `Delivery agent` — format `L\d{3}` (e.g. `L119`, `L228`)
- `Total price` — note: this is the **ordered** total, not deliverable
- `Order` — sequential order number per agent (1-indexed)

### 3.3 `Confirmed_deliveries_YYYY-MM-DD.xlsx`

Single sheet named `Confirmed deliveries`. 17 columns:

```
Code, Client name, Order date, Delivery Date, Phone number, Ville,
SalesRep_Name, SalesRep_PhoneNumber, Product code, Product name,
Ordered Qty, Deliverable Qty, Not Deliverable Qty, Stock (initial),
Price total Ordered, Price total Deliverable, Status
```

- One row per (Order, Product). An order with 6 products = 6 rows.
- `Product code` — joins to articles catalog
- `Status` — exactly one of: `'Delivered'`, `'Partial'`, `'Out of stock'`
- `Phone number` — stored as float in Excel (loses leading 0 for Moroccan numbers). Restore: prepend `'0'` if 9 digits and starts with 5, 6, or 7.
- `Order date` — string like `'18/04/2026 10:36:41'`. Format for display as `'DD-MM-YYYY HH:MM'`.

### 3.4 Manual-patch JSON (optional, for missing orders)

Sometimes Confirmed_deliveries excludes valid dispatched orders (we hit this once with 4 L229 orders). Provide a way to either:

(a) Detect missing orders (orders in dispatchers but not in confirmed) and show a UI form for the user to fill in, OR
(b) Accept a JSON upload of this shape:

```json
[
  {
    "Code": "CMD260413848",
    "Order date": "14/04/2026 18:38:00",
    "Delivery Date": "30/04/2026",
    "Client name": "Yassine hazzam",
    "Phone number": "0696741595",
    "Ville": "",
    "lines": [
      { "Product code": "ART03677", "Ordered Qty": 80, "Deliverable Qty": 80 },
      { "Product code": "ART03686", "Ordered Qty": 80, "Deliverable Qty": 0 }
    ]
  }
]
```

Mark these rows as patched, derive `Status` from qty (see §5.1), derive `Price total Ordered` as `qty × unit_price` where `unit_price` is computed by averaging `Price total Ordered / Ordered Qty` across other rows in the dataset for the same product code.

Either approach is fine — pick one.

---

## 4. Data flow / pipeline

```
   ┌─────────────────────┐
   │ Articles Matjar     │  (uploaded once → IndexedDB)
   │ (~4200 products)    │
   └──────────┬──────────┘
              │
              ▼ build PRODUCT_LOOKUP map
   ┌─────────────────────┐
   │ Code → {            │
   │   name_ar,          │
   │   unit,             │
   │   colisage,         │
   │   bc_carton,        │
   │   bc_unit           │
   │ }                   │
   └─────────────────────┘

   ┌─────────────────────┐    ┌──────────────────────────┐
   │ dispatchers.csv     │    │ confirmed_deliveries.xlsx│
   │ orders → agents     │    │ products per order       │
   └──────────┬──────────┘    └─────────────┬────────────┘
              │                              │
              └──────────────┬───────────────┘
                             ▼
              join on `Code`, attach `Delivery agent`
                             │
                             ▼
                ┌────────────────────────┐
                │ MERGED dataset         │  (one row per product line)
                │ + apply patches        │
                │ + verify reconciliation│
                └────────────┬───────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
   render bon de chargement       render bons de livraison
   (one PDF per agent,             (one PDF per agent, one
    aggregated per product)         page per order)
                │                         │
                └────────────┬────────────┘
                             ▼
                       ZIP & download
```

### 4.1 Building PRODUCT_LOOKUP from Articles Matjar

```js
const ATOMIC_UNIT_NAMES = {
  1: 'القرعة',
  2: 'الباكية',
  5: 'الحبة',
  6: 'الساشي',
  7: 'البيدو',
  10: 'الصاك',
};
const PACKING_UNIT_NAMES = {
  2: 'الكولية',
  3: 'الكرطونة',
  5: 'الصاك',
};

function clean(v) {
  if (v == null) return '';
  let s = String(v).trim();
  if (['na', 'null', 'nan', '0', '0.0'].includes(s.toLowerCase())) return '';
  if (s.endsWith('.0') && /^\d+\.0$/.test(s)) return s.slice(0, -2);
  return s;
}

function buildLookup(articles) {
  const lookup = new Map();
  for (const row of articles) {
    const code = clean(row['Code']);
    if (!code) continue;
    const sell = clean(row['Sell unit']);
    const au = row['Atomic unit'];
    const pu = row['Packing unit'];
    const pkgQty = row['Package quantity'];

    let unit = '';
    if (sell === 'ATOMIC' && ATOMIC_UNIT_NAMES[au]) {
      unit = ATOMIC_UNIT_NAMES[au];
    } else if (sell === 'PACKING' && PACKING_UNIT_NAMES[pu]) {
      unit = PACKING_UNIT_NAMES[pu];
    }

    let colisage = '';
    const parent = PACKING_UNIT_NAMES[pu];
    const child = ATOMIC_UNIT_NAMES[au];
    if (parent && child && pkgQty) {
      colisage = `${parent} = ${pkgQty} * ${child}`;
    }

    lookup.set(code, {
      name_ar: clean(row['Arabic description']),
      colisage,
      bc_carton: clean(row['Package barcode']),
      bc_unit: clean(row['Atomic barcode']),
      unit,
    });
  }
  return lookup;
}
```

### 4.2 Joining dispatchers + confirmed

```js
function mergeData(dispatchers, confirmed, patches = []) {
  const agentByCode = new Map(dispatchers.map(d => [d.Code, d['Delivery agent']]));

  // Apply patches: insert synthetic rows for orders not present in confirmed
  const patchRows = expandPatches(patches, confirmed);
  const allRows = [...confirmed, ...patchRows];

  // Attach delivery agent
  for (const row of allRows) {
    row.deliveryAgent = agentByCode.get(row.Code);
  }
  return allRows;
}
```

### 4.3 Reconciliation check (run before generating PDFs)

For every order code in confirmed, sum `Price total Ordered` across its rows. This must equal `dispatchers.Total price` for the same code. If it doesn't, surface a warning in the UI but still proceed.

Also: for every row, verify `Status` is consistent with `(Ordered Qty, Deliverable Qty)`:
- `Deliverable = 0` → expect `Out of stock`
- `Deliverable = Ordered` → expect `Delivered`
- `0 < Deliverable < Ordered` → expect `Partial`

---

## 5. Display rules (critical — these were derived through user iteration)

### 5.1 Three statuses, three behaviors

| Status | Quantity column | Price line | Counted in total? |
|---|---|---|---|
| **Delivered** | show `Deliverable Qty` | `Deliverable Qty × unit_price` | Yes |
| **Out of stock** | show `Ordered Qty` (whole row strikethrough in **black**) | show `Ordered Qty × unit_price` (also strikethrough) on bon de livraison; show `—` on bon de chargement | **No** |
| **Partial** | show `Deliverable Qty`, then below in red-text (but body should be black, see §5.4): `(غير مسلم: X)` where X = `Ordered − Deliverable` | `Deliverable Qty × unit_price` | Yes (only the deliverable portion) |

Strikethrough must be **black**, thickness 1.5px, applied to the whole row including the ART code line. When the row is OOS, the body of the row uses the same black color (the strikethrough is what conveys the status, not greying the text out).

### 5.2 المجموع (totals)

```
المجموع قبل الروميز  = sum of deliverable line totals (OOS lines contribute 0)
تمن الروميز            = .00
رسوم التوصيل           = .00
الضرائب والرسوم        = .00
المجموع بعد الروميز   = same as قبل الروميز (no discounts/fees applied)
```

The `.00` literals must appear with a leading dot to match the validated invoice canva format (Moroccan invoice style).

### 5.3 Footer notice (Arabic, on every invoice page)

```
الكميات الناقصة من الطلبيات سيتم توصيلها في عملية توصيل أخرى
يرجى تقديم أي شكوى خلال مدة أقصاها 48 ساعة منذ تاريخ استلام الطلب، حيث لن يتم النظر في أي شكوى بعد هذا التاريخ
للاستفسار، المرجو الاتصال بمصلحة التاجر على الرقم 0663866317 أو الرقم 0660043608 بعد الساعة 6 مساءً
للتواصل عبر الواتساب على الرقم 0608261111
```

### 5.4 Color rules

**Bon de Livraison (Z invoice template):**
- Header bar background: red `#e74c3c`, text white
- Grand total bar background: red `#e74c3c`, text white
- All other text/numbers/labels in tables and totals block: **pure black `#000`**
- No red, orange, or grey text — only black on white/cream backgrounds, and white text on red bars
- Logo: Z-in-circle image (provided as `zlogo.jpg`, see §6.4), 80×80px, top-right
- Light row striping: `#fdf6f5` for alternate rows

**Bon de Chargement (GOODEX yellow template):**
- Yellow accent bar: `#FFD966`, table header same yellow
- Total box `المجموع` = yellow `#FFD966`
- Two yellow signature boxes next to it
- Borders: `#d9d9d9` light grey
- Light row striping: `#f0effF`
- All body text: black
- Logo: same Z-in-circle, 80×80px, top-right (was previously the text "Awal" but we standardized on the Z logo)

### 5.5 Direction & fonts

```css
html { dir="rtl"; }
body {
  direction: rtl;
  font-family: 'Tajawal', 'Cairo', 'Noto Sans Arabic', Arial, sans-serif;
  color: #000;
}
td.product { text-align: right; }
td.product.ltr { direction: ltr; unicode-bidi: plaintext; }
```

Apply the `.ltr` class only when the displayed product name has no Arabic characters (fallback case for missing Arabic names — should be rare with Articles Matjar).

Detect Arabic presence:
```js
const isArabic = s => /[\u0600-\u06FF]/.test(s || '');
```

---

## 6. PDF templates (HTML structures)

The complete validated HTML templates are in `python_reference/build_invoices.py` and `python_reference/build_agent_pdfs_v3.py`. Key structures below — copy-paste these into JS template literals.

### 6.1 Bon de Livraison page structure (Z red invoice)

One HTML page **per order**. Each page is independent (uses `page-break-after: always`). Group all pages for one agent into a single multi-page HTML document, then convert to a single multi-page PDF.

```html
<div class="invoice-page">
  <div class="top">
    <div class="meta">
      <div class="meta-row"><span class="meta-label">نمرة الكموند</span><span class="meta-value">{code}</span></div>
      <div class="meta-row"><span class="meta-label">تاريخ الكموند</span><span class="meta-value">{order_date}</span></div>
      <div class="meta-row"><span class="meta-label">الكليان</span><span class="meta-value">{client}</span></div>
      <div class="meta-row"><span class="meta-label">رجل التوصيل</span><span class="meta-value">{agent}</span></div>
    </div>
    <div class="logo-wrap"><img class="logo-img" src="{LOGO_DATA_URL}" alt="Logo" /></div>
  </div>
  <div class="red-bar"></div>

  <table class="items">
    <thead>
      <tr>
        <th style="width:5%">#</th>
        <th style="width:48%">المنتوج</th>
        <th style="width:11%">الكمية</th>
        <th style="width:12%">الوحدة</th>
        <th style="width:11%">التمن</th>
        <th style="width:13%">المجموع</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>

  <div class="totals-wrap">
    <div class="totals">
      <div class="heading">المجموع</div>
      <div class="line"><span class="label">المجموع قبل الروميز</span><span class="val">{subtotal}</span></div>
      <div class="line"><span class="label">تمن الروميز</span><span class="val">.00</span></div>
      <div class="line"><span class="label">رسوم التوصيل</span><span class="val">.00</span></div>
      <div class="line"><span class="label">الضرائب والرسوم</span><span class="val">.00</span></div>
      <div class="grand"><span>المجموع بعد الروميز</span><span>{grand_total}</span></div>
    </div>
  </div>

  <div class="footer-notice">
    الكميات الناقصة من الطلبيات سيتم توصيلها في عملية توصيل أخرى<br>
    يرجى تقديم أي شكوى خلال مدة أقصاها 48 ساعة منذ تاريخ استلام الطلب، حيث لن يتم النظر في أي شكوى بعد هذا التاريخ<br>
    للاستفسار، المرجو الاتصال بمصلحة التاجر على الرقم 0663866317 أو الرقم 0660043608 بعد الساعة 6 مساءً<br>
    للتواصل عبر الواتساب على الرقم 0608261111
  </div>
</div>
```

Each row inside `<tbody>`:

```html
<tr class="{cls}">  <!-- cls is "oos" or "row-alt" or "" -->
  <td>{#}</td>
  <td class="product {ltr_class}"><span class="name">{display_name}</span><span class="ref">{art_code}</span></td>
  <td>{qty_html}</td>          <!-- includes partial-note span if applicable -->
  <td>{unit}</td>
  <td>{unit_price.toFixed(2)}</td>
  <td>{line_total.toFixed(2)}</td>
</tr>
```

For partial:
```js
qty_html = `${deliverable.toFixed(1)}<span class="partial-note">(غير مسلم: ${notDeliv})</span>`;
```

For OOS, show `Ordered Qty` (with `.toFixed(1)`) and apply strikethrough via the `oos` class on the `<tr>`. Line total cell shows `Ordered × unit_price` so the customer sees what was missing — strikethrough makes clear it wasn't delivered.

### 6.2 Bon de Livraison full CSS

```css
@page { size: A4; margin: 14mm 14mm 18mm 14mm; }

body {
  font-family: 'Tajawal', 'Cairo', 'Noto Sans Arabic', Arial, sans-serif;
  color: #000;
  direction: rtl;
  font-size: 10pt;
  margin: 0;
}

.invoice-page { page-break-after: always; padding-bottom: 10mm; }
.invoice-page:last-child { page-break-after: auto; }

.top {
  display: flex;
  flex-direction: row-reverse;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4mm;
}
.logo-wrap { text-align: left; }
.logo-img { width: 80px; height: 80px; object-fit: contain; display: inline-block; }

.red-bar { height: 2px; background: #e74c3c; margin: 0 0 6mm 0; }

.meta {
  text-align: left;
  direction: ltr;
  font-size: 10pt;
  line-height: 1.7;
}
.meta-row {
  display: flex;
  flex-direction: row-reverse;
  gap: 8mm;
  justify-content: flex-start;
}
.meta-label { color: #555; }
.meta-value { font-weight: 700; color: #000; font-style: italic; }

table.items {
  width: 100%;
  border-collapse: collapse;
  margin-top: 4mm;
  font-size: 9.5pt;
}
table.items thead th {
  background: #e74c3c;
  color: #fff;
  font-weight: 700;
  padding: 8px 6px;
  text-align: center;
  border: none;
}
table.items tbody td {
  background: #fff;
  color: #000;
  padding: 10px 6px;
  text-align: center;
  border-bottom: 1px solid #f3d6d3;
  vertical-align: middle;
}
table.items tbody tr.row-alt td { background: #fdf6f5; }

td.product { text-align: right; color: #000; }
td.product.ltr { direction: ltr; unicode-bidi: plaintext; }
td.product .name { display: block; color: #000; }
td.product .ref { display: block; color: #000; font-size: 9pt; margin-top: 3px; font-weight: 600; }

tr.oos td {
  color: #000;
  text-decoration: line-through;
  text-decoration-color: #000;
  text-decoration-thickness: 1.5px;
}
tr.oos td .name { color: #000; }
tr.oos td .ref {
  color: #000;
  text-decoration: line-through;
  text-decoration-color: #000;
}

.partial-note {
  color: #000;
  font-weight: 600;
  font-size: 8.5pt;
  display: block;
  margin-top: 2px;
  text-decoration: none;
}

.totals-wrap {
  display: flex;
  flex-direction: row-reverse;
  margin-top: 8mm;
}
.totals {
  margin-left: auto;
  width: 70mm;
  font-size: 10pt;
}
.totals .heading {
  font-weight: 800;
  font-size: 13pt;
  color: #000;
  text-align: right;
  margin-bottom: 4px;
}
.totals .line {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid #eee;
}
.totals .line .label { color: #000; }
.totals .line .val { font-weight: 700; color: #000; }
.totals .grand {
  background: #e74c3c;
  color: #fff;
  padding: 7px 12px;
  margin-top: 6px;
  display: flex;
  justify-content: space-between;
  font-weight: 700;
}

.footer-notice {
  position: relative;
  margin-top: 18mm;
  text-align: center;
  font-size: 8.5pt;
  color: #444;
  line-height: 1.7;
  border-top: 1px solid #eee;
  padding-top: 4mm;
}
```

### 6.3 Bon de Chargement page structure (yellow GOODEX)

One HTML page per agent. Aggregate rows by `Product code` across all that agent's orders (sum quantities and prices).

```html
<div class="page">
  <div class="header">
    <div class="meta">
      <div class="field">
        <span class="label">اسم رجل التوصيل</span>
        <span class="value">{agent}</span>
      </div>
      <div class="field">
        <span class="label">كود لبون دشارج</span>
        <span class="value">{discharge}</span>  <!-- e.g. L228_2026-04-30 -->
      </div>
      <div class="field">
        <span class="label">تاريخ التسليم</span>
        <span class="value">{delivery_date}</span>
      </div>
    </div>
    <div class="logo">
      <img class="logo-img" src="{LOGO_DATA_URL}" alt="Logo" />
    </div>
  </div>
  <div class="accent-bar"></div>

  <table>
    <thead>
      <tr>
        <th class="col-num">#</th>
        <th class="col-loc">موقع المنتوج</th>
        <th class="col-ref">المرجع</th>
        <th class="col-name">منتوج</th>
        <th class="col-pack">كوليساج</th>
        <th class="col-bcc">كود بار الكرتونة</th>
        <th class="col-bcu">كود بار الحبة</th>
        <th class="col-qty">الكمية</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>

  <div class="totals">
    <div class="total-block">
      <span class="label">المجموع</span>
      <span class="value">{total}</span>
    </div>
    <div class="signature-boxes">
      <div class="sig-box"></div>
      <div class="sig-box"></div>
    </div>
  </div>

  <div class="footer">
    <span>{agent}</span>
    <span>{delivery_date}</span>
  </div>
</div>
```

Row template:

```html
<tr class="{cls}">  <!-- "oos" or "row-alt" or "" -->
  <td>{#}</td>
  <td></td>  <!-- موقع المنتوج blank by default -->
  <td>{art_code}</td>
  <td class="product {ltr_class}">{display_name}</td>
  <td>{colisage}</td>
  <td>{bc_carton}</td>
  <td>{bc_unit}</td>
  <td>{qty_html}</td>  <!-- "X الكولية" or "X الكولية(غير مسلم: Y)" -->
</tr>
```

Quantity rendering for chargement:

```js
function fmtQty(deliverable, ordered, unit, status) {
  const u = unit ? ` ${unit}` : '';
  if (status === 'oos') return `${ordered}${u}`;
  if (status === 'partial') {
    const nd = ordered - deliverable;
    return `${deliverable}${u}<span class="partial-note">(غير مسلم: ${nd})</span>`;
  }
  return `${deliverable}${u}`;
}
```

### 6.4 Bon de Chargement full CSS

```css
@page { size: A4; margin: 14mm 12mm; }

body {
  font-family: 'Tajawal', 'Cairo', 'Noto Sans Arabic', Arial, sans-serif;
  color: #000;
  direction: rtl;
  font-size: 9.5pt;
  margin: 0;
}

.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }

.header {
  display: flex;
  flex-direction: row-reverse;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6mm;
}
.logo { text-align: left; }
.logo-img { width: 80px; height: 80px; object-fit: contain; display: inline-block; }

.meta {
  display: flex;
  flex-direction: row-reverse;
  gap: 24mm;
  flex: 1;
  margin-right: 6mm;
}
.meta .field { display: flex; flex-direction: column; gap: 2px; }
.meta .label { color: #888; font-size: 9pt; }
.meta .value { font-weight: 700; font-size: 11pt; color: #000; }

.accent-bar {
  height: 4px;
  background: #FFD966;
  width: 60mm;
  margin: 0 0 4mm auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  direction: rtl;
  font-size: 9pt;
}
th {
  background: #FFD966;
  color: #000;
  font-weight: 700;
  padding: 8px 4px;
  border: 1px solid #c9a635;
  text-align: center;
}
td {
  border: 1px solid #d9d9d9;
  padding: 7px 4px;
  text-align: center;
  vertical-align: middle;
  color: #000;
}
tr.row-alt td { background: #f0effF; }
td.product { text-align: right; color: #000; }
td.product.ltr { direction: ltr; unicode-bidi: plaintext; }

tr.oos td {
  color: #000;
  text-decoration: line-through;
  text-decoration-color: #000;
  text-decoration-thickness: 1.5px;
}

.partial-note {
  color: #000;
  font-weight: 600;
  font-size: 8pt;
  display: block;
  margin-top: 2px;
  text-decoration: none;
}

.totals {
  margin-top: 8mm;
  display: flex;
  flex-direction: row-reverse;
  justify-content: space-between;
  align-items: flex-start;
}
.total-block {
  background: #FFD966;
  border: 1px solid #c9a635;
  padding: 8px 18px;
  font-weight: 800;
  font-size: 12pt;
  min-width: 60mm;
  text-align: center;
  color: #000;
}
.total-block .label { float: right; }
.total-block .value { float: left; }
.signature-boxes { display: flex; gap: 6mm; }
.sig-box { width: 50mm; height: 28mm; border: 1.5px solid #FFD966; }

.footer {
  position: fixed;
  bottom: 6mm;
  left: 12mm;
  right: 12mm;
  display: flex;
  justify-content: space-between;
  font-size: 8.5pt;
  font-weight: 700;
}

th.col-num { width: 4%; }
th.col-loc { width: 8%; }
th.col-ref { width: 10%; }
th.col-name { width: 28%; }
th.col-pack { width: 14%; }
th.col-bcc { width: 11%; }
th.col-bcu { width: 11%; }
th.col-qty { width: 14%; }
```

### 6.5 Logo

The Z-in-circle logo is provided as `zlogo.jpg` (1024×1024 JPEG). Embed as base64 data URL:

```js
async function loadLogoAsDataURL(url) {
  const res = await fetch(url);
  const blob = await res.blob();
  return new Promise(resolve => {
    const r = new FileReader();
    r.onload = () => resolve(r.result);
    r.readAsDataURL(blob);
  });
}
const LOGO_DATA_URL = await loadLogoAsDataURL('/assets/zlogo.jpg');
```

Bake it into the bundled assets — it's small (~35KB).

---

## 7. PDF generation pipeline

```js
import html2pdf from 'html2pdf.js';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';

async function generateAllBons(merged, deliveryDate, logoDataUrl) {
  const agents = [...new Set(merged.map(r => r.deliveryAgent))].sort();

  const chargementZip = new JSZip();
  const livraisonZip = new JSZip();

  for (const agent of agents) {
    const agentRows = merged.filter(r => r.deliveryAgent === agent);

    // 1) Bon de chargement
    const chargementHtml = renderChargement(agent, agentRows, deliveryDate, logoDataUrl);
    const chargementBlob = await htmlToPdfBlob(chargementHtml);
    chargementZip.file(`${agent}_${deliveryDate}.pdf`, chargementBlob);

    // 2) Bon de livraison (multi-page, one page per order)
    const livraisonHtml = renderLivraison(agent, agentRows, deliveryDate, logoDataUrl);
    const livraisonBlob = await htmlToPdfBlob(livraisonHtml);
    livraisonZip.file(`invoices_${agent}_${deliveryDate}.pdf`, livraisonBlob);
  }

  const chargementZipBlob = await chargementZip.generateAsync({ type: 'blob' });
  const livraisonZipBlob = await livraisonZip.generateAsync({ type: 'blob' });

  saveAs(chargementZipBlob, `bons_chargement_${deliveryDate}.zip`);
  saveAs(livraisonZipBlob, `bons_livraison_${deliveryDate}.zip`);
}

async function htmlToPdfBlob(html) {
  // Create off-screen container so html2pdf can measure and rasterize
  const container = document.createElement('div');
  container.style.position = 'fixed';
  container.style.top = '-10000px';
  container.style.left = '0';
  container.style.width = '210mm';  // A4
  container.innerHTML = html;
  document.body.appendChild(container);

  try {
    const opts = {
      margin: [12, 10, 14, 10],  // mm: top, right, bottom, left
      filename: 'doc.pdf',
      image: { type: 'jpeg', quality: 0.95 },
      html2canvas: {
        scale: 2,           // crisp output
        useCORS: true,
        letterRendering: true,
      },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['css', 'legacy'] },
    };
    const blob = await html2pdf().set(opts).from(container).outputPdf('blob');
    return blob;
  } finally {
    container.remove();
  }
}
```

**Important:** when generating PDFs for many agents in a loop, `html2pdf` uses html2canvas which is heavy. Show a progress UI: `Generating... (3/6 agents)`. Each agent takes 1–3 seconds typically.

For best Arabic font rendering, ensure the Tajawal/Cairo/Noto Sans Arabic font is loaded **before** rasterization. Add to your global CSS:

```css
@font-face {
  font-family: 'Tajawal';
  src: url('/fonts/Tajawal-Regular.woff2') format('woff2');
  font-weight: 400;
  font-display: block;  /* important: don't render until loaded */
}
@font-face {
  font-family: 'Tajawal';
  src: url('/fonts/Tajawal-Bold.woff2') format('woff2');
  font-weight: 700;
  font-display: block;
}
```

Then await `document.fonts.ready` before invoking html2pdf:

```js
await document.fonts.ready;
```

---

## 8. Aggregation logic (bon de chargement only)

The bon de chargement aggregates lines per product across all of an agent's orders (one row per `Product code`, summing quantities and prices). The bon de livraison does NOT aggregate — it shows one row per order line.

```js
function aggregateForChargement(agentRows) {
  const byCode = new Map();
  for (const r of agentRows) {
    const code = r['Product code'];
    if (!byCode.has(code)) {
      byCode.set(code, {
        code,
        ordered: 0,
        deliverable: 0,
        priceDeliv: 0,
        frName: r['Product name'],
      });
    }
    const agg = byCode.get(code);
    agg.ordered += r['Ordered Qty'];
    agg.deliverable += r['Deliverable Qty'];
    if (r['Status'] !== 'Out of stock') {
      agg.priceDeliv += Number(r['Price total Deliverable'] || 0);
    }
  }

  // Derive aggregated status
  const result = [];
  for (const agg of byCode.values()) {
    let status;
    if (agg.deliverable === 0) status = 'oos';
    else if (agg.deliverable === agg.ordered) status = 'delivered';
    else status = 'partial';
    result.push({ ...agg, status });
  }
  return result;
}
```

For bon de livraison, render rows **as-is** from the merged dataset (one row per order line):

```js
function rowsForLivraison(orderLines) {
  return orderLines.map(r => ({
    code: r['Product code'],
    frName: r['Product name'],
    ordered: r['Ordered Qty'],
    deliverable: r['Deliverable Qty'],
    unitPrice: r['Ordered Qty'] > 0 ? r['Price total Ordered'] / r['Ordered Qty'] : 0,
    status: r['Status'].toLowerCase().replace(/\s+/g, '') === 'outofstock' ? 'oos'
          : r['Status'].toLowerCase() === 'partial' ? 'partial' : 'delivered',
  }));
}
```

---

## 9. Helpers

```js
// Strip leading zero on Moroccan phone (numbers stored as float in Excel lose it)
function fmtPhone(p) {
  if (p == null || p === '') return '';
  let s = String(p).trim();
  if (s.endsWith('.0')) s = s.slice(0, -2);
  if (/^\d{9}$/.test(s) && ['5', '6', '7'].includes(s[0])) s = '0' + s;
  return s;
}

// Format date "17/04/2026 10:36:41" → "17-04-2026 10:36"
function fmtOrderDate(raw) {
  if (!raw) return '';
  const s = String(raw).trim();
  // Try DD/MM/YYYY HH:MM(:SS)?
  const m = s.match(/^(\d{2})\/(\d{2})\/(\d{4})(?:\s+(\d{2}):(\d{2}))?/);
  if (m) {
    const [, d, mo, y, hh, mm] = m;
    return hh != null ? `${d}-${mo}-${y} ${hh}:${mm}` : `${d}-${mo}-${y} 00:00`;
  }
  // Fallback: try Date parsing
  const dt = new Date(s);
  if (!isNaN(dt)) {
    const pad = n => String(n).padStart(2, '0');
    return `${pad(dt.getDate())}-${pad(dt.getMonth() + 1)}-${dt.getFullYear()} ${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
  }
  return s;
}

function fmtMoney(n) {
  if (n == null || isNaN(n)) return '0.00';
  return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Build the client display string for invoice header
function fmtClient(name, phone) {
  const n = (name || '').trim();
  const p = fmtPhone(phone);
  if (n && p) return `${n} - ${p}`;
  if (n) return n;
  if (p) return p;
  return '—';
}
```

---

## 10. IndexedDB schema

Use `idb` library for promise-based access:

```js
import { openDB } from 'idb';

const DB_NAME = 'awal-deliveries';
const DB_VERSION = 1;

async function openStore() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains('articles')) {
        db.createObjectStore('articles', { keyPath: 'Code' });
      }
      if (!db.objectStoreNames.contains('meta')) {
        db.createObjectStore('meta');
      }
    },
  });
}

async function saveArticles(articles) {
  const db = await openStore();
  const tx = db.transaction(['articles', 'meta'], 'readwrite');
  await tx.objectStore('articles').clear();
  for (const row of articles) {
    if (row.Code) tx.objectStore('articles').put(row);
  }
  await tx.objectStore('meta').put(new Date().toISOString(), 'articles_uploaded_at');
  await tx.done;
}

async function loadArticles() {
  const db = await openStore();
  return db.getAll('articles');
}

async function getCatalogStatus() {
  const db = await openStore();
  const uploadedAt = await db.get('meta', 'articles_uploaded_at');
  const count = await db.count('articles');
  return { uploadedAt, count };
}
```

---

## 11. UI sketch (framework-agnostic)

```
┌─────────────────────────────────────────────────────────────┐
│ Awal — Daily Delivery Documents                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📦 Product Catalog                                         │
│  ✓ 4203 products loaded — last updated 2026-04-29           │
│  [ Update catalog ]                                         │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│  📅 Today's Delivery                                        │
│                                                             │
│  Delivery date: [ 2026-04-30 ]                              │
│                                                             │
│  Dispatchers CSV:    [ Choose file ] dispatchers-...csv ✓   │
│  Confirmed (XLSX):   [ Choose file ] Confirmed_...xlsx  ✓   │
│  Patches (optional): [ Choose file ] (none)                 │
│                                                             │
│  [ Validate & Preview ]                                     │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│  Preview                                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Agent │ Orders │ Lines │ Deliverable │ Anomalies   │    │
│  ├───────┼────────┼───────┼─────────────┼─────────────┤    │
│  │ L119  │   1    │   6   │  23,758.80  │             │    │
│  │ L216  │   4    │   9   │  38,587.20  │             │    │
│  │ L220  │   9    │   20  │ 100,964.74  │             │    │
│  │ ...   │        │       │             │             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  [ Download Bons de Chargement (ZIP) ]                      │
│  [ Download Bons de Livraison   (ZIP) ]                     │
│  [ Download Both                       ]                    │
│                                                             │
│  Or download individually:                                  │
│  L119: [chargement] [livraison]                             │
│  L216: [chargement] [livraison]                             │
│  ...                                                        │
└─────────────────────────────────────────────────────────────┘
```

The "Validate & Preview" step is critical. Compute:
- For each agent: `orderCount`, `lineCount`, `deliverableTotal`
- Per-order reconciliation: `sum(Price total Ordered for order) vs dispatchers.Total price` — flag mismatches > 0.01
- List of orders in dispatchers but not in confirmed (these need patches or will be silently dropped — surface them clearly)

---

## 12. Testing checklist (before considering done)

Test against the validated 2026-04-30 dataset:

- [ ] Agent totals match exactly: L119=23,758.80 / L216=38,587.20 / L220=100,964.74 / L222=85,767.90 / L228=53,382.70 / L229=75,225.65
- [ ] Total orders: 34 (1+4+9+9+6+5)
- [ ] Total lines: 97 (after L229 patch) or 86 (without patch)
- [ ] Status consistency: 0 mismatches between Status column and (Ordered, Deliverable) values
- [ ] Phone numbers display with leading 0 (e.g. `0721457817`, not `721457817.0`)
- [ ] OOS rows visually struck through with **black** line, not red
- [ ] Partial rows show `(غير مسلم: X)` underneath the deliverable qty
- [ ] Out-of-stock lines contribute 0 to المجموع قبل الروميز
- [ ] Footer includes the `الكميات الناقصة...` line above the 48-hour notice
- [ ] Bon de chargement footer (footer ID + page number)
- [ ] Bon de chargement — empty `موقع المنتوج` cells render as blank, not `null` or `NA`
- [ ] Arabic product names appear (not French) for all 51 products in the validated dataset
- [ ] Units in الكمية: الباكية for atomic-2, الحبة for atomic-5, البيدو for atomic-7, الكولية for packing-2, الكرطونة for packing-3, الصاك for packing-5
- [ ] Generated PDFs compared visually against `python_reference/sample_outputs/` (provided alongside this spec)

---

## 13. File deliverables to provide alongside this spec

When handing this off to Claude Code, also include in `python_reference/`:

- `build_invoices.py` — full Python source for bon de livraison (validated, golden truth)
- `build_agent_pdfs_v3.py` — full Python source for bon de chargement
- `sample_outputs/` — the 12 generated PDFs (6 chargement + 6 livraison) from the 2026-04-30 dataset
- `sample_inputs/` — copies of dispatchers.csv, Confirmed_deliveries.xlsx, Articles_Matjar.xlsx, zlogo.jpg
- `expected_totals.json` — per-agent and per-order expected totals for automated test verification

The Python scripts are the source of truth for any ambiguity — when in doubt, render with Python and match the output.

---

## 14. Edge cases & gotchas (do not skip)

1. **Phone numbers are floats in Excel** → leading zero loss. Always run through `fmtPhone()`.
2. **`Price total Ordered` can be NaN** for some OOS lines (e.g. ART00509 in the validated dataset). Compute unit price defensively: `qty > 0 && !isNaN(price) ? price / qty : 0`.
3. **Dispatcher's `Total price` = ordered total**, not deliverable. Don't use it as the invoice grand total. The grand total = `sum(Deliverable Qty × unit_price)` excluding OOS.
4. **CMD codes vary in length** (we've seen 11 and 12 digits). Use `/CMD\d+/` not a fixed length.
5. **Arabic text in PDF** — html2canvas relies on the browser's text rendering. If you see the wrong glyph shapes (disconnected letters), the font isn't loaded at rasterize time. Always `await document.fonts.ready` before `html2pdf().from(element)`.
6. **PDF text is rasterized**, so the resulting PDFs are not text-searchable. This matches the user's existing canva style. If text-searchable PDFs are ever required, switch to `pdf-lib` + a packaged Arabic font + a bidi/shaping library (significant rewrite).
7. **Bidi markers in pdftotext output** — irrelevant for the app, but if you ever extract text from generated PDFs for testing, strip `\u202a-\u202e` and `\u2066-\u2069`.
8. **`page-break-after: always`** must be on the page wrapper class for both templates so multi-order livraisons paginate correctly.
9. **A4 size** is 210×297mm. The off-screen container width must be 210mm exactly; otherwise html2canvas may misjudge layout.
10. **Don't include `<form>` tags** anywhere — submitting a form reloads the page and discards uploaded data. Use button click handlers instead.

---

## 15. Definition of done

The feature is complete when:

1. Uploading the three daily files produces ZIPs containing PDFs that match the Python golden outputs byte-perfect on totals (visual diff is fine; per-agent totals must equal exactly).
2. The catalog persists across page reloads.
3. The generation flow completes for the validated 2026-04-30 dataset in under 30 seconds on a mid-range laptop.
4. All edge cases in §14 are handled and demonstrated to work.
5. The UI shows clear progress and surfaces reconciliation warnings before generating.
