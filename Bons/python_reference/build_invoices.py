"""Generate per-agent invoice PDFs — one page per order — in red Z template style."""
import pandas as pd
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

DELIVERIES = '/mnt/user-data/outputs/deliveries_merged_2026-04-30.xlsx'
LOOKUP_NEW = '/mnt/user-data/uploads/goodex_all_deliveries.xlsx'
LOOKUP_OLD = '/mnt/user-data/outputs/livraisons_GOODEX_2026-04-29.xlsx'
ARTICLES = '/mnt/user-data/uploads/Export_Articles_Matjar_2026-04-29__1_.xlsx'
OUT_DIR = Path('/mnt/user-data/outputs/invoices')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Unit code → Arabic name (per Sell unit context)
ATOMIC_UNIT_NAMES = {
    1: 'الحبة',
    2: 'الباكية',
    5: 'الحبة',
    7: 'البيدو',
}
PACKING_UNIT_NAMES = {
    2: 'الكولية',
    3: 'الكرطونة',
    5: 'الصاك',
}

# === Build product → unit lookup ===
def clean(v):
    if pd.isna(v): return ''
    s = str(v).strip()
    if s.lower() in ('na', 'null', 'nan', '0', '0.0'): return ''
    if s.endswith('.0') and s[:-2].isdigit(): return s[:-2]
    return s

UNIT_LOOKUP = {}     # ART code → unit (الكولية/البيدو/الحبة...)
NAME_AR_LOOKUP = {}  # ART code → Arabic product name

# Primary source: Articles Matjar export — comprehensive, has Arabic names + unit codes
articles = pd.read_excel(ARTICLES, sheet_name='Products')
for _, row in articles.iterrows():
    code = clean(row['Code'])
    if not code: continue
    ar = clean(row['Arabic description'])
    if ar:
        NAME_AR_LOOKUP[code] = ar
    sell = clean(row['Sell unit'])
    if sell == 'ATOMIC':
        au = row['Atomic unit']
        if pd.notna(au) and int(au) in ATOMIC_UNIT_NAMES:
            UNIT_LOOKUP[code] = ATOMIC_UNIT_NAMES[int(au)]
    elif sell == 'PACKING':
        pu = row['Packing unit']
        if pd.notna(pu) and int(pu) in PACKING_UNIT_NAMES:
            UNIT_LOOKUP[code] = PACKING_UNIT_NAMES[int(pu)]

# Secondary: goodex_all_deliveries (overrides only if Articles didn't have data)
new_lookup = pd.read_excel(LOOKUP_NEW, sheet_name='All Deliveries')
for _, row in new_lookup.iterrows():
    code = clean(row['Reference'])
    if not code: continue
    if code not in UNIT_LOOKUP:
        UNIT_LOOKUP[code] = clean(row['Unit'])
    if code not in NAME_AR_LOOKUP:
        NAME_AR_LOOKUP[code] = clean(row['Product'])

old_lookup = pd.read_excel(LOOKUP_OLD, sheet_name='الكل')
for _, row in old_lookup.iterrows():
    code = clean(row['المرجع'])
    if not code: continue
    if code not in UNIT_LOOKUP:
        qty_str = clean(row['الكمية'])
        unit = ''
        if ' ' in qty_str:
            parts = qty_str.split()
            if len(parts) >= 2:
                unit = parts[1]
        if unit:
            UNIT_LOOKUP[code] = unit
    if code not in NAME_AR_LOOKUP:
        NAME_AR_LOOKUP[code] = clean(row['منتوج'])

# Fallback unit map for products not in lookup — pick reasonable defaults from confirmed file
# (ART codes from L229 invoices already shown in canva)
INVOICE_UNIT_HINTS = {
    'ART04001': 'الحبة',  # canva CMD260424519
    'ART03687': 'البيدو',
    'ART03688': 'البيدو',
    'ART03686': 'البيدو',
    'ART03679': 'البيدو',
    'ART03677': 'البيدو',
    'ART03164': 'الكولية',
}
for k, v in INVOICE_UNIT_HINTS.items():
    if not UNIT_LOOKUP.get(k):
        UNIT_LOOKUP[k] = v

# === Load deliveries ===
df = pd.read_excel(DELIVERIES, sheet_name='All products')
def norm_status(s):
    s = str(s).strip().lower()
    if s == 'delivered': return 'delivered'
    if s == 'out of stock': return 'oos'
    if s == 'partial': return 'partial'
    return 'unknown'
df['_status'] = df['Status'].map(norm_status)

def fmt_order_date(raw):
    """Convert '17/04/2026 10:36:41' → '17-04-2026 10:36'"""
    if pd.isna(raw): return ''
    s = str(raw).strip()
    # Try ISO and dd/mm/yyyy formats
    for fmt in ('%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'):
        try:
            dt = pd.to_datetime(s, format=fmt)
            return dt.strftime('%d-%m-%Y %H:%M')
        except (ValueError, TypeError):
            continue
    try:
        dt = pd.to_datetime(s)
        return dt.strftime('%d-%m-%Y %H:%M')
    except Exception:
        return s

def fmt_phone(p):
    if pd.isna(p): return ''
    s = str(p).strip()
    if s.endswith('.0'): s = s[:-2]
    # Add leading 0 for Moroccan mobile numbers if missing
    if s.isdigit() and len(s) == 9 and s[0] in ('5', '6', '7'):
        s = '0' + s
    return s

def fmt_num(n, decimals=2):
    if pd.isna(n): return '0.00'
    return f'{n:,.{decimals}f}'

def fmt_qty(q):
    """1.0 → '1.0', 200 → '200.0' to match canva style"""
    return f'{float(q):.1f}'


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8" />
<title>{title}</title>
<style>
  @page {{ size: A4; margin: 14mm 14mm 18mm 14mm; }}
  body {{
    font-family: 'Tajawal', 'Cairo', 'Noto Sans Arabic', Arial, sans-serif;
    color: #000;
    direction: rtl;
    font-size: 10pt;
    margin: 0;
  }}
  .invoice-page {{ page-break-after: always; padding-bottom: 10mm; }}
  .invoice-page:last-child {{ page-break-after: auto; }}

  .top {{
    display: flex;
    flex-direction: row-reverse;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 4mm;
  }}
  .logo-wrap {{
    text-align: left;
  }}
  .logo-img {{
    width: 80px;
    height: 80px;
    object-fit: contain;
    display: inline-block;
  }}

  .red-bar {{
    height: 2px;
    background: #e74c3c;
    margin: 0 0 6mm 0;
  }}

  .meta {{
    text-align: left;
    direction: ltr;
    font-size: 10pt;
    line-height: 1.7;
  }}
  .meta-row {{ display: flex; flex-direction: row-reverse; gap: 8mm; justify-content: flex-start; }}
  .meta-label {{ color: #555; }}
  .meta-value {{ font-weight: 700; color: #000; font-style: italic; }}

  table.items {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 4mm;
    font-size: 9.5pt;
  }}
  table.items thead th {{
    background: #e74c3c;
    color: #fff;
    font-weight: 700;
    padding: 8px 6px;
    text-align: center;
    border: none;
  }}
  table.items tbody td {{
    background: #fff;
    color: #000;
    padding: 10px 6px;
    text-align: center;
    border-bottom: 1px solid #f3d6d3;
    vertical-align: middle;
  }}
  table.items tbody tr.row-alt td {{ background: #fdf6f5; }}

  td.product {{ text-align: right; color: #000; }}
  td.product.ltr {{ direction: ltr; unicode-bidi: plaintext; }}
  td.product .name {{ display: block; color: #000; }}
  td.product .ref {{ display: block; color: #000; font-size: 9pt; margin-top: 3px; font-weight: 600; }}

  /* Out-of-stock row strikethrough */
  tr.oos td {{
    color: #000;
    text-decoration: line-through;
    text-decoration-color: #000;
    text-decoration-thickness: 1.5px;
  }}
  tr.oos td .name {{ color: #000; }}
  tr.oos td .ref {{ color: #000; text-decoration: line-through; text-decoration-color: #000; }}

  /* Partial qty note */
  .partial-note {{
    color: #000;
    font-weight: 600;
    font-size: 8.5pt;
    display: block;
    margin-top: 2px;
    text-decoration: none;
  }}

  /* Totals block */
  .totals-wrap {{
    display: flex;
    flex-direction: row-reverse;
    margin-top: 8mm;
  }}
  .totals {{
    margin-left: auto;
    width: 70mm;
    font-size: 10pt;
  }}
  .totals .heading {{
    font-weight: 800;
    font-size: 13pt;
    color: #000;
    text-align: right;
    margin-bottom: 4px;
  }}
  .totals .line {{
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px solid #eee;
  }}
  .totals .line .label {{ color: #000; }}
  .totals .line .val {{ font-weight: 700; color: #000; }}
  .totals .grand {{
    background: #e74c3c;
    color: #fff;
    padding: 7px 12px;
    margin-top: 6px;
    display: flex;
    justify-content: space-between;
    font-weight: 700;
  }}

  .footer-notice {{
    position: relative;
    margin-top: 18mm;
    text-align: center;
    font-size: 8.5pt;
    color: #444;
    line-height: 1.7;
    border-top: 1px solid #eee;
    padding-top: 4mm;
  }}
</style>
</head>
<body>
{pages}
</body>
</html>
"""

PAGE_TEMPLATE = """
<div class="invoice-page">
  <div class="top">
    <div class="meta">
      <div class="meta-row"><span class="meta-label">نمرة الكموند</span><span class="meta-value">{code}</span></div>
      <div class="meta-row"><span class="meta-label">تاريخ الكموند</span><span class="meta-value">{order_date}</span></div>
      <div class="meta-row"><span class="meta-label">الكليان</span><span class="meta-value">{client}</span></div>
      <div class="meta-row"><span class="meta-label">رجل التوصيل</span><span class="meta-value">{agent}</span></div>
    </div>
    <div class="logo-wrap"><img class="logo-img" src="data:image/jpeg;base64,__LOGO_B64__" alt="Logo" /></div>
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
    <tbody>
      {rows}
    </tbody>
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
"""

def is_arabic(text):
    if not text: return False
    return any('\u0600' <= ch <= '\u06FF' for ch in text)

def build_qty_cell(deliverable, ordered, status):
    if status == 'oos':
        return fmt_qty(ordered)  # strikethrough applied to whole row
    if status == 'partial':
        not_deliv = ordered - deliverable
        return f'{fmt_qty(deliverable)}<span class="partial-note">(غير مسلم: {int(not_deliv)})</span>'
    return fmt_qty(deliverable)

def build_order_page(order_rows, agent):
    """order_rows is the dataframe slice for one CMD order."""
    first = order_rows.iloc[0]
    code = first['Code']
    order_date = fmt_order_date(first['Order date'])
    client_name = clean(first['Client name'])
    phone = fmt_phone(first['Phone number'])
    if client_name and phone:
        client = f'{client_name} - {phone}'
    elif client_name:
        client = client_name
    elif phone:
        client = phone
    else:
        client = '—'

    rows_html = []
    subtotal = 0.0
    for i, (_, r) in enumerate(order_rows.iterrows()):
        status = r['_status']
        ordered = int(r['Ordered Qty'])
        deliverable = int(r['Deliverable Qty'])
        unit_price = (r['Price total Ordered'] / ordered) if ordered > 0 else 0
        # line total: deliverable × unit price
        line_total_deliv = deliverable * unit_price
        # for OOS, show what would have been (strikethrough)
        if status == 'oos':
            display_line_total = ordered * unit_price
            display_qty_for_total = ordered
        else:
            display_line_total = line_total_deliv
            display_qty_for_total = deliverable
            subtotal += line_total_deliv

        # Product name: prefer Arabic from lookup
        ar_name = NAME_AR_LOOKUP.get(r['Product code'], '')
        display_name = ar_name if ar_name else r['Product name']
        name_class = 'product' if is_arabic(display_name) else 'product ltr'

        unit = UNIT_LOOKUP.get(r['Product code'], '')

        cls = 'oos' if status == 'oos' else ('row-alt' if i % 2 else '')
        qty_html = build_qty_cell(deliverable, ordered, status)

        rows_html.append(
            f'<tr class="{cls}">'
            f'<td>{i+1}</td>'
            f'<td class="{name_class}"><span class="name">{display_name}</span><span class="ref">{r["Product code"]}</span></td>'
            f'<td>{qty_html}</td>'
            f'<td>{unit}</td>'
            f'<td>{fmt_num(unit_price)}</td>'
            f'<td>{fmt_num(display_line_total)}</td>'
            f'</tr>'
        )

    return PAGE_TEMPLATE.format(
        code=code,
        order_date=order_date,
        client=client,
        agent=agent,
        rows='\n'.join(rows_html),
        subtotal=fmt_num(subtotal),
        grand_total=fmt_num(subtotal),
    )


async def render():
    # Load logo as base64
    with open('/home/claude/zlogo_b64.txt') as f:
        logo_b64 = f.read().strip()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        agents = sorted(df['Delivery agent'].unique())
        for agent in agents:
            sub = df[df['Delivery agent'] == agent]
            order_codes = sub['Code'].drop_duplicates().tolist()
            pages = []
            agent_total = 0.0
            for code in order_codes:
                order_rows = sub[sub['Code'] == code]
                pages.append(build_order_page(order_rows, agent))
                # accumulate deliverable subtotal for logging
                for _, r in order_rows.iterrows():
                    if r['_status'] != 'oos':
                        ordered = int(r['Ordered Qty'])
                        deliv = int(r['Deliverable Qty'])
                        unit_p = (r['Price total Ordered'] / ordered) if ordered > 0 else 0
                        agent_total += deliv * unit_p

            html = HTML_TEMPLATE.format(title=f'Invoices {agent}', pages='\n'.join(pages))
            html = html.replace('__LOGO_B64__', logo_b64)
            html_path = OUT_DIR / f'invoices_{agent}.html'
            html_path.write_text(html, encoding='utf-8')
            page = await browser.new_page()
            await page.goto(f'file://{html_path.resolve()}')
            pdf_path = OUT_DIR / f'invoices_{agent}_2026-04-30.pdf'
            await page.pdf(path=str(pdf_path), format='A4', print_background=True,
                          margin={'top': '12mm', 'bottom': '14mm', 'left': '12mm', 'right': '12mm'})
            await page.close()
            print(f'  {pdf_path.name}: {len(order_codes)} orders / pages, deliverable total {agent_total:,.2f}')
        await browser.close()

asyncio.run(render())
