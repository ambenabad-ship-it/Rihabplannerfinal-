"""Generate per-agent GOODEX PDFs (bon de chargement) using Articles Matjar as primary lookup."""
import pandas as pd
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

DELIVERIES = '/mnt/user-data/outputs/deliveries_merged_2026-04-30.xlsx'
LOOKUP_NEW = '/mnt/user-data/uploads/goodex_all_deliveries.xlsx'
LOOKUP_OLD = '/mnt/user-data/outputs/livraisons_GOODEX_2026-04-29.xlsx'
ARTICLES = '/mnt/user-data/uploads/Export_Articles_Matjar_2026-04-29__1_.xlsx'
DISPATCHERS = '/mnt/user-data/uploads/dispatchers-2026-04-30.csv'
OUT_DIR = Path('/mnt/user-data/outputs/agent_sheets')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Unit code → Arabic name (derived from articles + goodex cross-reference)
ATOMIC_UNIT_NAMES = {
    1: 'القرعة', 2: 'الباكية', 5: 'الحبة',
    6: 'الساشي', 7: 'البيدو', 10: 'الصاك',
}
PACKING_UNIT_NAMES = {
    2: 'الكولية', 3: 'الكرطونة', 5: 'الصاك',
}

def clean(v):
    if pd.isna(v):
        return ''
    s = str(v).strip()
    if s.lower() in ('na', 'null', 'nan', '0', '0.0'):
        return ''
    if s.endswith('.0') and s[:-2].isdigit():
        return s[:-2]
    return s

PRODUCT_LOOKUP = {}  # code → {name_ar, colisage, bc_carton, bc_unit, unit}

# === Primary source: Articles Matjar (4203 products, full Arabic names) ===
articles = pd.read_excel(ARTICLES, sheet_name='Products')
for _, row in articles.iterrows():
    code = clean(row['Code'])
    if not code:
        continue
    name_ar = clean(row['Arabic description'])
    bc_atomic = clean(row['Atomic barcode'])
    bc_package = clean(row['Package barcode'])
    sell = clean(row['Sell unit'])
    pkg_qty = row['Package quantity']
    au = row['Atomic unit']
    pu = row['Packing unit']
    
    # Determine the displayed unit (matches what canva invoices/sheets show)
    if sell == 'ATOMIC' and pd.notna(au) and int(au) in ATOMIC_UNIT_NAMES:
        unit = ATOMIC_UNIT_NAMES[int(au)]
    elif sell == 'PACKING' and pd.notna(pu) and int(pu) in PACKING_UNIT_NAMES:
        unit = PACKING_UNIT_NAMES[int(pu)]
    else:
        unit = ''
    
    # Build colisage string: "PARENT = MULT * CHILD"
    colisage = ''
    parent_name = PACKING_UNIT_NAMES.get(int(pu)) if pd.notna(pu) else None
    child_name = ATOMIC_UNIT_NAMES.get(int(au)) if pd.notna(au) else None
    if parent_name and child_name and pd.notna(pkg_qty):
        colisage = f'{parent_name} = {int(pkg_qty)} * {child_name}'
    
    PRODUCT_LOOKUP[code] = {
        'name_ar': name_ar,
        'colisage': colisage,
        'bc_carton': bc_package,
        'bc_unit': bc_atomic,
        'unit': unit,
    }

# === Augment with goodex_all_deliveries (only fields that are missing) ===
new_lookup = pd.read_excel(LOOKUP_NEW, sheet_name='All Deliveries')
for _, row in new_lookup.iterrows():
    code = clean(row['Reference'])
    if not code:
        continue
    if code not in PRODUCT_LOOKUP:
        PRODUCT_LOOKUP[code] = {'name_ar': '', 'colisage': '', 'bc_carton': '', 'bc_unit': '', 'unit': ''}
    p = PRODUCT_LOOKUP[code]
    if not p['name_ar']: p['name_ar'] = clean(row['Product'])
    if not p['colisage']: p['colisage'] = clean(row['Colisage'])
    if not p['bc_carton']: p['bc_carton'] = clean(row['Barcode Carton'])
    if not p['bc_unit']: p['bc_unit'] = clean(row['Barcode Unit'])
    if not p['unit']: p['unit'] = clean(row['Unit'])

# === Augment with old livraisons file (only fields still missing) ===
old_lookup = pd.read_excel(LOOKUP_OLD, sheet_name='الكل')
for _, row in old_lookup.iterrows():
    code = clean(row['المرجع'])
    if not code:
        continue
    if code not in PRODUCT_LOOKUP:
        PRODUCT_LOOKUP[code] = {'name_ar': '', 'colisage': '', 'bc_carton': '', 'bc_unit': '', 'unit': ''}
    p = PRODUCT_LOOKUP[code]
    if not p['name_ar']: p['name_ar'] = clean(row['منتوج'])
    if not p['colisage']: p['colisage'] = clean(row['كوليساج'])
    if not p['bc_carton']: p['bc_carton'] = clean(row['كود بار الكرتونة'])
    if not p['bc_unit']: p['bc_unit'] = clean(row['كود بار الحبة'])
    if not p['unit']:
        qty_str = clean(row['الكمية'])
        if ' ' in qty_str:
            parts = qty_str.split()
            if len(parts) >= 2:
                p['unit'] = parts[1]

# === Build agent → discharge code map (LXXX_YYYY-MM-DD) ===
disp = pd.read_csv(DISPATCHERS)
delivery_date_str = '2026-04-30'

# === Load deliveries ===
df = pd.read_excel(DELIVERIES, sheet_name='All products')
def norm_status(s):
    s = str(s).strip().lower()
    if s == 'delivered': return 'delivered'
    if s == 'out of stock': return 'oos'
    if s == 'partial': return 'partial'
    return 'unknown'
df['_status'] = df['Status'].map(norm_status)

# Aggregate to one line per (agent, product) — sum qty/price across orders
def aggregate_for_agent(sub):
    rows = []
    grouped = sub.groupby('Product code', sort=False)
    for code, g in grouped:
        # If a product has mixed statuses across orders, treat as partial
        ordered_total = int(g['Ordered Qty'].sum())
        deliv_total = int(g['Deliverable Qty'].sum())
        if deliv_total == 0:
            status = 'oos'
        elif deliv_total == ordered_total:
            status = 'delivered'
        else:
            status = 'partial'
        price_deliv = float(g['Price total Deliverable'].sum())
        # Pick a fallback name from raw data
        fr_name = g['Product name'].iloc[0]
        rows.append({
            'code': code,
            'fr_name': fr_name,
            'ordered': ordered_total,
            'deliverable': deliv_total,
            'price_deliv': price_deliv,
            'status': status,
        })
    return rows


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8" />
<title>{agent}</title>
<style>
  @page {{ size: A4; margin: 14mm 12mm; }}
  body {{
    font-family: 'Tajawal', 'Cairo', 'Noto Sans Arabic', Arial, sans-serif;
    color: #000;
    direction: rtl;
    font-size: 9.5pt;
    margin: 0;
  }}
  .header {{
    display: flex;
    flex-direction: row-reverse;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 6mm;
  }}
  .logo {{ text-align: left; }}
  .logo-img {{
    width: 80px;
    height: 80px;
    object-fit: contain;
    display: inline-block;
  }}
  .meta {{
    display: flex;
    flex-direction: row-reverse;
    gap: 24mm;
    flex: 1;
    margin-right: 6mm;
  }}
  .meta .field {{ display: flex; flex-direction: column; gap: 2px; }}
  .meta .label {{ color: #888; font-size: 9pt; }}
  .meta .value {{ font-weight: 700; font-size: 11pt; }}
  .accent-bar {{
    height: 4px;
    background: #FFD966;
    width: 60mm;
    margin: 0 0 4mm auto;
  }}
  table {{ width: 100%; border-collapse: collapse; direction: rtl; font-size: 9pt; }}
  th {{
    background: #FFD966;
    color: #000;
    font-weight: 700;
    padding: 8px 4px;
    border: 1px solid #c9a635;
    text-align: center;
  }}
  td {{
    border: 1px solid #d9d9d9;
    padding: 7px 4px;
    text-align: center;
    vertical-align: middle;
  }}
  tr.row-alt td {{ background: #f0effF; }}
  td.product {{ text-align: right; }}
  td.product.ltr {{ direction: ltr; unicode-bidi: plaintext; }}

  tr.oos td {{
    color: #888;
    text-decoration: line-through;
    text-decoration-color: #c0392b;
    text-decoration-thickness: 1.5px;
  }}
  .partial-note {{
    color: #c0392b;
    font-weight: 600;
    font-size: 8pt;
    display: block;
    margin-top: 2px;
    text-decoration: none;
  }}
  .totals {{
    margin-top: 8mm;
    display: flex;
    flex-direction: row-reverse;
    justify-content: space-between;
    align-items: flex-start;
  }}
  .total-block {{
    background: #FFD966;
    border: 1px solid #c9a635;
    padding: 8px 18px;
    font-weight: 800;
    font-size: 12pt;
    min-width: 60mm;
    text-align: center;
  }}
  .total-block .label {{ float: right; }}
  .total-block .value {{ float: left; }}
  .signature-boxes {{ display: flex; gap: 6mm; }}
  .sig-box {{ width: 50mm; height: 28mm; border: 1.5px solid #FFD966; }}
  .footer {{
    position: fixed;
    bottom: 6mm;
    left: 12mm;
    right: 12mm;
    display: flex;
    justify-content: space-between;
    font-size: 8.5pt;
    font-weight: 700;
  }}
  th.col-num {{ width: 4%; }}
  th.col-loc {{ width: 8%; }}
  th.col-ref {{ width: 10%; }}
  th.col-name {{ width: 28%; }}
  th.col-pack {{ width: 14%; }}
  th.col-bcc {{ width: 11%; }}
  th.col-bcu {{ width: 11%; }}
  th.col-qty {{ width: 14%; }}
</style>
</head>
<body>
<div class="header">
  <div class="meta">
    <div class="field">
      <span class="label">اسم رجل التوصيل</span>
      <span class="value">{agent}</span>
    </div>
    <div class="field">
      <span class="label">كود لبون دشارج</span>
      <span class="value">{discharge}</span>
    </div>
    <div class="field">
      <span class="label">تاريخ التسليم</span>
      <span class="value">{delivery_date}</span>
    </div>
  </div>
  <div class="logo">
    <img class="logo-img" src="data:image/jpeg;base64,__LOGO_B64__" alt="Logo" />
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
  <tbody>
    {rows}
  </tbody>
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
</body>
</html>
"""

def fmt_qty(deliverable, ordered, unit, status):
    unit_suffix = f' {unit}' if unit else ''
    if status == 'oos':
        return f'{ordered}{unit_suffix}'  # strikethrough applied to whole row
    if status == 'partial':
        not_deliv = ordered - deliverable
        return f'{deliverable}{unit_suffix}<span class="partial-note">(غير مسلم: {not_deliv})</span>'
    return f'{deliverable}{unit_suffix}'

def is_arabic(text):
    if not text:
        return False
    for ch in text:
        if '\u0600' <= ch <= '\u06FF':
            return True
    return False

def build_rows(agg_rows):
    html_rows = []
    for i, r in enumerate(agg_rows):
        info = PRODUCT_LOOKUP.get(r['code'], {})
        name_ar = info.get('name_ar', '')
        # Use Arabic name if available, otherwise fallback to French/English
        display_name = name_ar if name_ar else r['fr_name']
        name_class = 'product' if is_arabic(display_name) else 'product ltr'
        cls = 'oos' if r['status'] == 'oos' else ('row-alt' if i % 2 else '')
        qty_html = fmt_qty(r['deliverable'], r['ordered'], info.get('unit', ''), r['status'])
        html_rows.append(
            f'<tr class="{cls}">'
            f'<td>{i+1}</td>'
            f'<td></td>'  # موقع المنتوج — always blank
            f'<td>{r["code"]}</td>'
            f'<td class="{name_class}">{display_name}</td>'
            f'<td>{info.get("colisage", "")}</td>'
            f'<td>{info.get("bc_carton", "")}</td>'
            f'<td>{info.get("bc_unit", "")}</td>'
            f'<td>{qty_html}</td>'
            f'</tr>'
        )
    return '\n'.join(html_rows)


async def render():
    # Load logo as base64
    with open('/home/claude/zlogo_b64.txt') as f:
        logo_b64 = f.read().strip()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        agents = sorted(df['Delivery agent'].unique())
        for agent in agents:
            sub = df[df['Delivery agent'] == agent]
            agg_rows = aggregate_for_agent(sub)
            total = sum(r['price_deliv'] for r in agg_rows)
            discharge = f'{agent}_{delivery_date_str}'
            html = HTML_TEMPLATE.format(
                agent=agent,
                discharge=discharge,
                delivery_date=delivery_date_str,
                rows=build_rows(agg_rows),
                total=f'{total:,.2f}',
            )
            html = html.replace('__LOGO_B64__', logo_b64)
            html_path = OUT_DIR / f'{agent}.html'
            html_path.write_text(html, encoding='utf-8')
            page = await browser.new_page()
            await page.goto(f'file://{html_path.resolve()}')
            pdf_path = OUT_DIR / f'{agent}_2026-04-30.pdf'
            await page.pdf(path=str(pdf_path), format='A4', print_background=True,
                          margin={'top': '12mm', 'bottom': '12mm', 'left': '10mm', 'right': '10mm'})
            await page.close()
            with_arabic = sum(1 for r in agg_rows if PRODUCT_LOOKUP.get(r['code'], {}).get('name_ar'))
            print(f'Generated {pdf_path.name}  — {len(agg_rows)} products ({with_arabic} with Arabic data), total {total:,.2f}')
        await browser.close()

asyncio.run(render())
