"""Product Basket Analysis - Online Retail II (Python + Pandas)
Finds products frequently bought together using order (invoice) IDs.
Self-pairs are excluded (only unordered pairs A<B)."""
import pandas as pd, numpy as np
from scipy import sparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MIN_INVOICES = 40   # product must appear in at least this many orders
TOP_N = 15

raw = pd.read_csv("data/online_retail_II.csv", encoding="latin1")
raw.columns = [c.strip() for c in raw.columns]
stats = {"raw_rows": len(raw)}

# ---------- 1. Cleaning ----------
df = raw.copy()
df["Invoice"] = df["Invoice"].astype(str)
df["StockCode"] = df["StockCode"].astype(str).str.strip().str.upper()
df = df[~df["Invoice"].str.startswith(("C", "A"))]            # cancellations / adjustments
stats["after_cancel"] = len(df)
df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]
stats["after_qty_price"] = len(df)
non_product = {"POST", "DOT", "M", "BANK CHARGES", "PADS", "AMAZONFEE", "CRUK", "D", "S", "B"}
df = df[~df["StockCode"].isin(non_product)]
df = df[df["StockCode"].str.match(r"^\d{5}")]                  # real product codes only
stats["after_nonproduct"] = len(df)
df["Description"] = df["Description"].astype(str).str.strip()

# one name per stock code (most frequent description)
names = (df.groupby("StockCode")["Description"]
           .agg(lambda s: s.value_counts().index[0]))

# one row per (order, product) - a product counts once per basket
basket = df[["Invoice", "StockCode"]].drop_duplicates()
stats["orders"] = basket["Invoice"].nunique()
stats["products"] = basket["StockCode"].nunique()
sizes = basket.groupby("Invoice").size()
stats["avg_basket"] = round(sizes.mean(), 1)
stats["single_item_orders"] = int((sizes == 1).sum())
basket = basket[basket["Invoice"].isin(sizes[sizes >= 2].index)]   # pairs need >=2 items
stats["multi_item_orders"] = basket["Invoice"].nunique()

# keep products with enough support
freq = basket["StockCode"].value_counts()
keep = freq[freq >= MIN_INVOICES].index
basket = basket[basket["StockCode"].isin(keep)]
stats["products_kept"] = len(keep)

# ---------- 2. Order x Product matrix and pair counts ----------
inv_codes, inv_idx = np.unique(basket["Invoice"], return_inverse=True)
prod_codes, prod_idx = np.unique(basket["StockCode"], return_inverse=True)
X = sparse.csr_matrix((np.ones(len(basket), dtype=np.int32), (inv_idx, prod_idx)),
                      shape=(len(inv_codes), len(prod_codes)))
co = (X.T @ X).tocoo()
mask = co.row < co.col                                          # exclude self-pairs, avoid A-B / B-A duplicates
pairs = pd.DataFrame({"a": prod_codes[co.row[mask]], "b": prod_codes[co.col[mask]],
                      "pair_orders": co.data[mask]})
N = len(inv_codes)
cnt = pd.Series(np.asarray(X.sum(axis=0)).ravel(), index=prod_codes)
pairs["count_a"] = pairs["a"].map(cnt).values
pairs["count_b"] = pairs["b"].map(cnt).values
pairs["support_%"] = (pairs["pair_orders"] / N * 100).round(3)
pairs["conf_a_to_b_%"] = (pairs["pair_orders"] / pairs["count_a"] * 100).round(1)
pairs["conf_b_to_a_%"] = (pairs["pair_orders"] / pairs["count_b"] * 100).round(1)
pairs["lift"] = (pairs["pair_orders"] * N / (pairs["count_a"] * pairs["count_b"])).round(2)
pairs["product_a"] = pairs["a"].map(names)
pairs["product_b"] = pairs["b"].map(names)
pairs = pairs.sort_values("pair_orders", ascending=False).reset_index(drop=True)
stats["pairs_total"] = len(pairs)
stats["N_matrix_orders"] = N

top_freq = pairs.head(TOP_N)
top_lift = pairs[pairs["pair_orders"] >= 60].sort_values("lift", ascending=False).head(TOP_N)
top_products = (cnt.sort_values(ascending=False).head(10)
                   .rename_axis("StockCode").reset_index(name="orders"))
top_products["Description"] = top_products["StockCode"].map(names)

cols = ["a","product_a","b","product_b","pair_orders","support_%","conf_a_to_b_%","conf_b_to_a_%","lift"]
pairs[cols].head(100).to_csv("outputs/top_100_pairs_by_frequency.csv", index=False)
top_lift[cols].to_csv("outputs/top_pairs_by_lift.csv", index=False)
top_products.to_csv("outputs/top_products.csv", index=False)

# ---------- 3. Charts ----------
def short(s, n=34): return s if len(s) <= n else s[:n-1] + "…"
t = top_freq.iloc[::-1]
labels = [f"{short(a,26)} + {short(b,26)}" for a, b in zip(t.product_a.str.title(), t.product_b.str.title())]
plt.figure(figsize=(10, 6)); plt.barh(labels, t.pair_orders, color="#1f4e8c")
plt.xlabel("Orders containing both products"); plt.title("Top 15 Product Pairs Bought Together")
plt.tight_layout(); plt.savefig("images/top_pairs.png", dpi=150); plt.close()

t = top_lift.head(10).iloc[::-1]
labels = [f"{short(a,26)} + {short(b,26)}" for a, b in zip(t.product_a.str.title(), t.product_b.str.title())]
plt.figure(figsize=(10, 5)); plt.barh(labels, t.lift, color="#e8730c")
plt.xlabel("Lift"); plt.title("Top 10 Pairs by Lift (min. 60 co-orders)")
plt.tight_layout(); plt.savefig("images/top_lift.png", dpi=150); plt.close()

import json; json.dump(stats, open("outputs/stats.json", "w"), indent=1)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 40)
print(stats); print(top_freq[cols]); print(top_lift[cols]); print(top_products)
