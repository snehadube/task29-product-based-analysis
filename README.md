# Product Basket Analysis (Online Retail II)

Find products that are frequently purchased together using **Python + Pandas** — an introduction to association-style (market-basket) analysis.
Built as part of my **Data Analytics internship at Veda Technology**.

## Objective
Identify the top product pairs bought together in the same order and turn them into practical business recommendations (bundling, cross-sell, merchandising, stock planning).

## Dataset
Online Retail II (UK online gift-ware retailer) — 541,910 transaction rows, 19,773 valid orders, 3,791 products after cleaning.
> The CSV is not included in this repo because of its size. Download it (Kaggle / UCI "Online Retail II") and put it at `data/online_retail_II.csv`.

## Approach
1. **Clean:** removed cancelled invoices (`C…`), adjustments (`A…`), quantity/price <= 0, and non-product codes (POST, DOT, M, BANK CHARGES…).
2. **Basket = order ID.** Each product counted once per invoice (de-duplicated).
3. **Order x product matrix** (sparse) -> co-occurrence counts for every product pair.
4. **Exclude self-pairs** and count each pair once (A-B = B-A).
5. Kept products appearing in >= 40 orders; ranked pairs by frequency and **lift**.
6. Metrics: pair orders, support, confidence (A->B, B->A), lift.

## Key Findings
- Most frequent pair: **Jumbo Bag Pink Polkadot + Jumbo Bag Red Retrospot** — 825 orders (4.5% of baskets).
- **Regency teacup & saucer** colours (Green / Roses / Pink) are bought together, lift ≈ 13–15.
- **Lunch bag** designs cluster around Lunch Bag Red Retrospot (560–655 orders per pair).
- Highest lift: matching **colour variants** (Kids Rain Mac Blue + Pink, lift ≈ 156) and complementary items (Bicycle Clips + Puncture Repair Kit, lift ≈ 129).

## Recommendations
Bundles / multi-buy offers · "Frequently bought together" widgets · cross-sell complementary items · place paired items together · replenish paired stock together · targeted email recommendations.

## Project Structure
```
├── basket_analysis.py                  # cleaning + pair analysis + charts
├── make_report.py                      # builds the PDF report
├── Product_Basket_Analysis_Report.pdf  # final project report
├── outputs/                            # top pairs CSVs (frequency, lift), top products, stats
├── images/                             # charts
├── requirements.txt
└── README.md
```

## How to Run
```bash
pip install -r requirements.txt
python basket_analysis.py     # creates outputs/ and images/
python make_report.py         # creates the PDF
```

## Interview Notes
- **What is market-basket analysis?** Finding items frequently bought together in the same transaction (association rules: support, confidence, lift).
- **Why use order ID?** The order ID defines a basket; customer ID or date would mix separate purchases and create false pairs.

## Limitations / Next Steps
Wholesale-heavy data; association ≠ causation; low-volume high-lift pairs can be noisy. Next: Apriori/FP-Growth for 3+ item rules, segment by country, check seasonality.

## Author
Sneha — Data Analytics Track, Veda Technology
