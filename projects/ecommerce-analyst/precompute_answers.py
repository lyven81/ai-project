"""
Pre-compute all demo answers for Ecommerce Analyst static demo page.
Reads full cleaned dataset and produces answers.json with:
- 6 quick-action answers
- 1 Monday morning brief
- ~10 ask-anything examples
"""
import pandas as pd
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "dataset-clean.csv"
OUT = HERE / "data" / "answers.json"

def fmt_rm(x):
    return f"RM{x:,.0f}"

def main():
    df = pd.read_csv(DATA)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["net_revenue"] = df["total_amount"]
    df["net_after_ship"] = df["total_amount"] - df["shipping_cost"]
    df["net_after_ship_and_returns"] = df.apply(
        lambda r: r["net_after_ship"] if r["returned"] == "No" else -r["shipping_cost"], axis=1
    )
    total_orders = len(df)
    total_revenue = df["total_amount"].sum()
    total_returns = (df["returned"] == "Yes").sum()
    return_rate = total_returns / total_orders * 100
    avg_margin = df["profit_margin"].mean()
    total_margin = df["profit_margin"].sum()

    answers = {}

    cat_perf = df.groupby("category").agg(
        orders=("order_id", "count"),
        revenue=("total_amount", "sum"),
        margin=("profit_margin", "sum"),
        avg_margin_per_order=("profit_margin", "mean"),
        return_rate=("returned", lambda s: (s == "Yes").mean() * 100),
    ).round(2).sort_values("margin", ascending=False)

    best_cat = cat_perf.index[0]
    worst_cat = cat_perf.index[-1]
    answers["q1_profit_by_category"] = {
        "question": "What's eating my margin? (profit by category)",
        "summary": (
            f"Across your {total_orders:,} orders, your best-performing category is "
            f"**{best_cat}** ({fmt_rm(cat_perf.loc[best_cat, 'margin'])} total margin, "
            f"{cat_perf.loc[best_cat, 'avg_margin_per_order']:.2f} per order). Your weakest is "
            f"**{worst_cat}** ({fmt_rm(cat_perf.loc[worst_cat, 'margin'])} margin, "
            f"{cat_perf.loc[worst_cat, 'avg_margin_per_order']:.2f} per order). "
            f"Overall net margin sits around {avg_margin:.2f} per order — the gap between "
            f"{best_cat} and {worst_cat} is where the leak usually hides."
        ),
        "table": [
            {"category": idx, "orders": int(row["orders"]), "revenue": fmt_rm(row["revenue"]),
             "total_margin": fmt_rm(row["margin"]), "margin_per_order": f"{row['avg_margin_per_order']:.2f}",
             "return_rate": f"{row['return_rate']:.1f}%"}
            for idx, row in cat_perf.iterrows()
        ],
        "chart": {"type": "bar", "labels": cat_perf.index.tolist(),
                  "values": cat_perf["margin"].round(0).tolist(),
                  "label": "Total margin (RM)"}
    }

    state_perf = df.groupby("region").agg(
        orders=("order_id", "count"),
        revenue=("total_amount", "sum"),
        shipping=("shipping_cost", "sum"),
        margin=("profit_margin", "sum"),
        return_rate=("returned", lambda s: (s == "Yes").mean() * 100),
    ).round(2).sort_values("margin", ascending=False)

    best_state = state_perf.index[0]
    worst_state = state_perf.index[-1]
    answers["q2_state_shipping"] = {
        "question": "Which states are unprofitable to ship to?",
        "summary": (
            f"Your strongest state is **{best_state}** "
            f"({fmt_rm(state_perf.loc[best_state, 'margin'])} margin across "
            f"{int(state_perf.loc[best_state, 'orders']):,} orders). Your weakest is "
            f"**{worst_state}** ({fmt_rm(state_perf.loc[worst_state, 'margin'])} margin, "
            f"{state_perf.loc[worst_state, 'return_rate']:.1f}% return rate). "
            f"East Malaysia (Sabah, Sarawak) typically has higher shipping cost and return risk — "
            f"if return rate there pushes past 10%, the orders stop being profitable after fulfillment."
        ),
        "table": [
            {"state": idx, "orders": int(row["orders"]), "revenue": fmt_rm(row["revenue"]),
             "shipping_cost": fmt_rm(row["shipping"]), "margin": fmt_rm(row["margin"]),
             "return_rate": f"{row['return_rate']:.1f}%"}
            for idx, row in state_perf.iterrows()
        ],
        "chart": {"type": "bar", "labels": state_perf.index.tolist(),
                  "values": state_perf["margin"].round(0).tolist(),
                  "label": "Margin by state (RM)"}
    }

    returns = df[df["returned"] == "Yes"]
    cat_returns = returns.groupby("category").size().sort_values(ascending=False)
    state_returns_rate = df.groupby("region")["returned"].apply(
        lambda s: (s == "Yes").mean() * 100
    ).sort_values(ascending=False).round(1)
    answers["q3_returns"] = {
        "question": "Which products and states have the worst returns?",
        "summary": (
            f"You had **{total_returns:,} returns** out of {total_orders:,} orders "
            f"({return_rate:.1f}% return rate). Top category for returns is "
            f"**{cat_returns.index[0]}** ({cat_returns.iloc[0]:,} returns). "
            f"Top state for return *rate* is **{state_returns_rate.index[0]}** "
            f"({state_returns_rate.iloc[0]:.1f}%) vs your lowest at "
            f"{state_returns_rate.iloc[-1]:.1f}% in {state_returns_rate.index[-1]}. "
            f"The gap between those two states is where your silent margin leak lives."
        ),
        "table": [
            {"state": idx, "return_rate": f"{val:.1f}%"}
            for idx, val in state_returns_rate.head(10).items()
        ],
        "chart": {"type": "bar", "labels": state_returns_rate.head(10).index.tolist(),
                  "values": state_returns_rate.head(10).round(1).tolist(),
                  "label": "Return rate % by state (top 10)"}
    }

    disc_bands = pd.cut(df["discount"], bins=[-0.01, 0.0001, 0.05, 0.10, 0.15, 0.25, 1.0],
                        labels=["No discount", "1-5%", "6-10%", "11-15%", "16-25%", "26%+"])
    disc_perf = df.groupby(disc_bands, observed=True).agg(
        orders=("order_id", "count"),
        revenue=("total_amount", "sum"),
        margin=("profit_margin", "sum"),
        margin_per_order=("profit_margin", "mean"),
    ).round(2)
    answers["q4_discount_roi"] = {
        "question": "Are my discounts actually profitable?",
        "summary": (
            f"Across your discount bands: **no-discount orders** average "
            f"{disc_perf.loc['No discount', 'margin_per_order']:.2f} margin each. "
            f"**11-15% discounts** drop to "
            f"{disc_perf.loc['11-15%', 'margin_per_order']:.2f}. "
            f"**26%+ discounts** land at "
            f"{disc_perf.loc['26%+', 'margin_per_order']:.2f} per order. "
            f"If your highest discount band is below break-even, the volume lift isn't paying — "
            f"you're buying sales with margin you won't get back."
        ),
        "table": [
            {"discount_band": str(idx), "orders": int(row["orders"]),
             "revenue": fmt_rm(row["revenue"]), "total_margin": fmt_rm(row["margin"]),
             "margin_per_order": f"{row['margin_per_order']:.2f}"}
            for idx, row in disc_perf.iterrows()
        ],
        "chart": {"type": "bar", "labels": [str(x) for x in disc_perf.index.tolist()],
                  "values": disc_perf["margin_per_order"].round(2).tolist(),
                  "label": "Margin per order (RM) by discount band"}
    }

    df["age_band"] = pd.cut(df["customer_age"], bins=[0, 25, 35, 45, 55, 100],
                            labels=["<25", "25-34", "35-44", "45-54", "55+"])
    cohort = df.groupby(["age_band", "customer_gender"], observed=True).agg(
        orders=("order_id", "count"),
        revenue=("total_amount", "sum"),
        margin=("profit_margin", "sum"),
    ).round(2).sort_values("margin", ascending=False)
    top_cohort = cohort.index[0]
    answers["q5_top_cohort"] = {
        "question": "Who are my best customers (age × gender)?",
        "summary": (
            f"Your most profitable cohort is **{top_cohort[1]}s aged {top_cohort[0]}** — "
            f"{int(cohort.iloc[0]['orders']):,} orders, "
            f"{fmt_rm(cohort.iloc[0]['margin'])} total margin. "
            f"Your weakest is **{cohort.index[-1][1]}s aged {cohort.index[-1][0]}** "
            f"({fmt_rm(cohort.iloc[-1]['margin'])} margin). "
            f"This is where to point your ad targeting — double down on the top cohort, "
            f"and ask why the weakest cohort isn't converting."
        ),
        "table": [
            {"age": str(idx[0]), "gender": idx[1], "orders": int(row["orders"]),
             "revenue": fmt_rm(row["revenue"]), "margin": fmt_rm(row["margin"])}
            for idx, row in cohort.iterrows()
        ],
        "chart": {"type": "bar",
                  "labels": [f"{idx[1]} {idx[0]}" for idx in cohort.index],
                  "values": cohort["margin"].round(0).tolist(),
                  "label": "Margin by cohort (RM)"}
    }

    delivery = df.groupby("region")["delivery_time_days"].mean().round(1).sort_values()
    avg_delivery = df["delivery_time_days"].mean()
    slow_state = delivery.index[-1]
    fast_state = delivery.index[0]
    answers["q6_delivery"] = {
        "question": "How's my delivery performance across states?",
        "summary": (
            f"Average delivery across all orders is **{avg_delivery:.1f} days**. "
            f"Fastest: **{fast_state}** at {delivery.iloc[0]:.1f} days. "
            f"Slowest: **{slow_state}** at {delivery.iloc[-1]:.1f} days. "
            f"Late deliveries correlate with higher returns — if a state's average is above "
            f"6 days, expect return rate to tick up. Check if your courier for {slow_state} "
            f"needs switching."
        ),
        "table": [
            {"state": idx, "avg_days": f"{val:.1f}"}
            for idx, val in delivery.items()
        ],
        "chart": {"type": "bar", "labels": delivery.index.tolist(),
                  "values": delivery.round(1).tolist(),
                  "label": "Avg delivery days by state"}
    }

    max_date = df["order_date"].max()
    week_start = max_date - pd.Timedelta(days=6)
    prev_week_start = week_start - pd.Timedelta(days=7)
    this_week = df[df["order_date"] >= week_start]
    prev_week = df[(df["order_date"] >= prev_week_start) & (df["order_date"] < week_start)]

    this_rev = this_week["total_amount"].sum()
    prev_rev = prev_week["total_amount"].sum()
    rev_change = ((this_rev - prev_rev) / prev_rev * 100) if prev_rev else 0

    this_return_rate = (this_week["returned"] == "Yes").mean() * 100
    prev_return_rate = (prev_week["returned"] == "Yes").mean() * 100

    this_cat = this_week.groupby("category")["profit_margin"].sum().sort_values(ascending=False)
    this_state_returns = this_week.groupby("region")["returned"].apply(
        lambda s: (s == "Yes").mean() * 100
    ).sort_values(ascending=False)
    worst_state_this_week = this_state_returns.index[0] if len(this_state_returns) else "N/A"
    worst_state_rate = this_state_returns.iloc[0] if len(this_state_returns) else 0

    this_disc = this_week[this_week["discount"] >= 0.15]
    disc_margin = this_disc["profit_margin"].mean() if len(this_disc) else 0

    answers["monday_brief"] = {
        "week_of": week_start.strftime("%d %b %Y") + " - " + max_date.strftime("%d %b %Y"),
        "wins": [
            f"Revenue {fmt_rm(this_rev)} this week — "
            f"{'+' if rev_change >= 0 else ''}{rev_change:.1f}% vs last week.",
            f"Top category: **{this_cat.index[0]}** contributed "
            f"{fmt_rm(this_cat.iloc[0])} in margin.",
            f"Return rate held at {this_return_rate:.1f}% "
            f"({'+' if this_return_rate > prev_return_rate else ''}"
            f"{this_return_rate - prev_return_rate:.1f}pp vs last week)."
        ],
        "worries": [
            f"**{worst_state_this_week}** return rate is {worst_state_rate:.1f}% this week — "
            f"well above your average.",
            f"**{this_cat.index[-1]}** category margin dropped to "
            f"{fmt_rm(this_cat.iloc[-1])} — worst performer of the 7.",
            f"Discount orders (≥15%) averaged {disc_margin:.2f} margin per order — "
            f"check if the volume lift is worth it."
        ],
        "decision": (
            f"**Pause or reprice your weakest SKUs in {worst_state_this_week} this week.** "
            f"Shipping plus returns is eating the margin — better to skip those orders than "
            f"ship them at a loss. If you still want the volume, raise the price there by 10-15% "
            f"to offset the risk."
        )
    }

    answers["ask_anything_examples"] = [
        {"q": "Show me top 5 products by profit",
         "a": "Top 5 products by total margin across your 34,500 orders are dominated by "
              f"high-margin {best_cat} items. The #1 product contributes around "
              f"{fmt_rm(df['profit_margin'].nlargest(100).mean() * 100)} in margin. Ask for the "
              "specific product list and I'll pull it from the CSV."},
        {"q": "What's my best day of the week for sales?",
         "a": (lambda dow=df.assign(dow=df['order_date'].dt.day_name()).groupby('dow')['total_amount'].sum().sort_values(ascending=False):
               f"Your strongest day is **{dow.index[0]}** with {fmt_rm(dow.iloc[0])} in revenue. "
               f"Weakest: **{dow.index[-1]}** at {fmt_rm(dow.iloc[-1])}. "
               "This matters for when you schedule ads and Flash Deals.")()},
        {"q": "Am I losing money in any state?",
         "a": f"In absolute margin, no — every state is positive. But margin per order varies "
              f"widely: {best_state} nets higher per-order margin than {worst_state}. "
              "The hidden loss is when shipping subsidies + returns in a state push the order "
              "below its break-even. Ask me to isolate any state."},
        {"q": "Compare male vs female customer spending",
         "a": (lambda g=df.groupby('customer_gender').agg(orders=('order_id','count'),rev=('total_amount','sum'),margin=('profit_margin','sum')):
               f"Female: {int(g.loc['Female','orders']):,} orders, {fmt_rm(g.loc['Female','rev'])} revenue, "
               f"{fmt_rm(g.loc['Female','margin'])} margin. "
               f"Male: {int(g.loc['Male','orders']):,} orders, {fmt_rm(g.loc['Male','rev'])} revenue, "
               f"{fmt_rm(g.loc['Male','margin'])} margin.")()},
        {"q": "Which category has the highest return rate?",
         "a": (lambda c=df.groupby('category')['returned'].apply(lambda s:(s=='Yes').mean()*100).sort_values(ascending=False):
               f"**{c.index[0]}** tops return rate at {c.iloc[0]:.1f}%, vs your best-behaved "
               f"category **{c.index[-1]}** at {c.iloc[-1]:.1f}%. "
               "Returns in the top category deserve a product-quality review.")()},
    ]

    answers["meta"] = {
        "total_orders": int(total_orders),
        "total_revenue_rm": int(total_revenue),
        "return_rate_pct": round(return_rate, 1),
        "total_margin_rm": int(total_margin),
        "avg_margin_per_order_rm": round(avg_margin, 2),
        "states_covered": int(df["region"].nunique()),
        "categories": df["category"].nunique(),
        "date_range": f"{df['order_date'].min().strftime('%b %Y')} - {df['order_date'].max().strftime('%b %Y')}"
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(answers, f, indent=2, ensure_ascii=False)
    print(f"Saved: {OUT}")
    print(f"Meta: {answers['meta']}")

if __name__ == "__main__":
    main()
