import json, pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

s = json.load(open("outputs/stats.json"))
freq = pd.read_csv("outputs/top_100_pairs_by_frequency.csv").head(10)
lift = pd.read_csv("outputs/top_pairs_by_lift.csv").head(8)
tp = pd.read_csv("outputs/top_products.csv").head(5)

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=colors.HexColor("#1f3a6e"), fontSize=16, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=colors.HexColor("#e8730c"), fontSize=12, spaceBefore=8, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10, leading=14)
SM = ParagraphStyle("SM", parent=B, fontSize=7.5, leading=9)
SMH = ParagraphStyle("SMH", parent=SM, textColor=colors.white, fontName="Helvetica-Bold")
TITLE = ParagraphStyle("T", parent=ss["Title"], textColor=colors.HexColor("#1f3a6e"), fontSize=24, leading=28)
def P(t, st=B): return Paragraph(t, st)
def bullets(items): return [P("&bull; " + i) for i in items]
def tbl(data, widths, hdr=colors.HexColor("#1f3a6e")):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),hdr),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTSIZE",(0,0),(-1,-1),7.5),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#f2f5fa")]),
        ("GRID",(0,0),(-1,-1),0.3,colors.grey)]))
    return t

doc = SimpleDocTemplate("Product_Basket_Analysis_Report.pdf", pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="Product Basket Analysis", author="Sneha")
E = []
E += [Spacer(1, 0.5*cm), P("Product Basket Analysis", TITLE), Spacer(1, 6),
      P("Finding products frequently purchased together using Python &amp; Pandas", ss["Heading3"]),
      Spacer(1, 10),
      P("Dataset: Online Retail II (UK-based online gift-ware retailer)<br/>"
        "Tools: Python, Pandas, SciPy, Matplotlib<br/>"
        "Prepared by: Sneha | Data Analytics Track, Veda Technology<br/>Date: 06 Oct 2026"),
      Spacer(1, 1*cm)]
E += [P("1. Objective &amp; Approach", H1),
      P("The goal is an introduction to association-style (market-basket) analysis: find which products "
        "customers buy together in the same order, so the business can cross-sell, bundle and place products better. "
        "The <b>order (invoice) ID</b> is the basket: all items sharing an invoice were bought together."),
      P("Method", H2)]
E += bullets([
  "Cleaned data: removed cancelled invoices (start with C), adjustments (A), non-positive quantity/price, and non-product codes (POST, DOT, M, BANK CHARGES, etc.).",
  "Counted each product <b>once per order</b> (de-duplicated invoice-product rows).",
  "Built an order x product matrix and counted co-occurrence of every product pair.",
  "<b>Excluded self-pairs</b> and counted each pair once (A-B = B-A) by keeping only code(A) &lt; code(B).",
  "Kept products present in at least 40 orders to avoid noise; ranked pairs by frequency and by lift."])
E += [P("Metrics", H2)]
E += bullets([
  "<b>Pair orders</b>: number of orders containing both products.",
  "<b>Support</b>: pair orders / total orders. <b>Confidence (A&rarr;B)</b>: of orders with A, % that also have B.",
  "<b>Lift</b>: confidence / base popularity of B. Lift &gt; 1 means the products appear together more than chance."])
E += [P("2. Data Overview &amp; Cleaning", H1)]
cl = [["Step","Rows / Orders"],
  ["Raw rows", f"{s['raw_rows']:,}"],
  ["After removing cancellations / adjustments", f"{s['after_cancel']:,}"],
  ["After removing qty/price &lt;= 0", f"{s['after_qty_price']:,}"],
  ["After removing non-product codes (final)", f"{s['after_nonproduct']:,}"],
  ["Orders (baskets) / unique products", f"{s['orders']:,} / {s['products']:,}"],
  ["Average basket size (unique items)", f"{s['avg_basket']}"],
  ["Single-item orders (cannot form pairs)", f"{s['single_item_orders']:,}"],
  ["Orders analysed (2+ items, frequent products)", f"{s['N_matrix_orders']:,}"],
  ["Products analysed / pairs evaluated", f"{s['products_kept']:,} / {s['pairs_total']:,}"]]
cl = [[P(c, SMH if ri==0 else SM) for c in r] for ri,r in enumerate(cl)]
E += [tbl(cl, [10*cm, 6*cm]), PageBreak()]

E += [P("3. Top Product Pairs", H1), P("Most frequent pairs (by number of orders containing both items):", B), Spacer(1,4)]
rows = [["#","Product A","Product B","Orders","Support %","Conf A&rarr;B %","Conf B&rarr;A %","Lift"]]
for i, r in freq.iterrows():
    rows.append([str(i+1), r.product_a.title(), r.product_b.title(), int(r.pair_orders), r["support_%"], r["conf_a_to_b_%"], r["conf_b_to_a_%"], r.lift])
rows = [[P(str(c), SMH if ri==0 else SM) for c in r] for ri,r in enumerate(rows)]
E += [tbl(rows, [0.8*cm,4.4*cm,4.4*cm,1.3*cm,1.4*cm,1.6*cm,1.6*cm,1.5*cm]), Spacer(1,8),
      Image("images/top_pairs.png", width=16*cm, height=9.6*cm), PageBreak()]

E += [P("4. Strongest Associations (by Lift)", H1),
      P("Lift shows how much more often two items are bought together than expected by chance (pairs with at least 60 co-orders):"), Spacer(1,4)]
rows = [["Product A (code)","Product B (code)","Orders","Conf A&rarr;B %","Conf B&rarr;A %","Lift"]]
for _, r in lift.iterrows():
    rows.append([f"{r.product_a.title()} ({r.a})", f"{r.product_b.title()} ({r.b})", int(r.pair_orders), r["conf_a_to_b_%"], r["conf_b_to_a_%"], r.lift])
rows = [[P(str(c), SMH if ri==0 else SM) for c in r] for ri,r in enumerate(rows)]
E += [tbl(rows, [4.9*cm,4.9*cm,1.3*cm,1.8*cm,1.8*cm,1.6*cm]), Spacer(1,8),
      Image("images/top_lift.png", width=15*cm, height=7.5*cm)]
E += [P("5. Key Insights", H1)]
E += bullets([
  "<b>Jumbo bags travel together.</b> Jumbo Bag Pink Polkadot + Jumbo Bag Red Retrospot is the most frequent pair (825 orders, 4.5% of baskets); 68% of Pink Polkadot buyers also bought Red Retrospot.",
  "<b>Regency teacup sets are bought as a collection.</b> Green, Roses and Pink Regency Teacup &amp; Saucer pair with each other in 600-770 orders each, with lift of 13-15 (13-15x more than chance).",
  "<b>Lunch bag designs cluster.</b> Lunch Bag Red Retrospot pairs with Suki, Black Skull, Pink Polkadot and Spaceboy designs (560-655 orders each): customers buy several designs at once.",
  "<b>Colour/variant pairs have the highest lift</b> (Kids Rain Mac Blue + Pink: lift 156; Child's Garden Spade/Trowel Blue + Pink: lift 120-137). Customers buy matching variants together.",
  "<b>Complementary products also appear:</b> Classic Bicycle Clips + Bicycle Puncture Repair Kit (80 orders, lift 129) and Fruit Salad Paper Cups + Paper Plates (81 orders, lift 137).",
  "High-lift pairs are small in volume; high-frequency pairs have lower lift but bigger revenue impact. Both views are useful."])
E += [PageBreak(), P("6. Recommendations", H1)]
E += bullets([
  "<b>Create bundles / multi-buy offers</b> for jumbo bag, lunch bag and Regency teacup families (e.g. 'buy 3 designs, save 10%').",
  "<b>Add 'Frequently bought together' and 'Complete the set' blocks</b> on product pages and in the cart using the top pairs table.",
  "<b>Cross-sell complementary items</b>: bicycle clips with repair kit, paper cups with paper plates.",
  "<b>Merchandise and pick-pack together</b>: place high-affinity items side by side (website category pages, catalogue, warehouse picking zones).",
  "<b>Stock planning</b>: forecast and replenish paired items together so one out-of-stock variant does not kill the whole basket.",
  "<b>Email campaigns</b>: after a customer buys one item of a pair, recommend the partner product."])
E += [P("7. Limitations &amp; Next Steps", H1)]
E += bullets([
  "Data is from a wholesale-heavy retailer; many orders are bulk buys by trade customers, so patterns may differ for individual shoppers.",
  "Association is not causation; test recommendations with A/B experiments. Lift on low-volume pairs can be unstable (a minimum order threshold was used).",
  "Next steps: apply Apriori / FP-Growth (mlxtend) for 3+ item rules, segment by country or customer type, and check seasonality."])
E += [P("8. Interview Questions", H1),
  P("<b>What is market-basket analysis?</b> A data-mining technique that finds items frequently bought together in the same transaction, expressed as association rules (A &rarr; B) with support, confidence and lift. It is used for cross-selling, bundling, store layout and recommendations."),
  Spacer(1,4),
  P("<b>Why use order ID?</b> The order ID defines a basket: products with the same order ID were bought together in a single purchase. Using customer ID or date instead would mix separate purchases and create false pairs. Counting each product once per order and excluding self-pairs keeps the counts correct."),
  Spacer(1,10), P("<i>Code, data outputs and charts: see the GitHub repository (basket_analysis.py).</i>", SM)]
doc.build(E)
