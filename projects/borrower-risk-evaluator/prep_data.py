"""
Borrower Risk Evaluator - keyless data prep.

Reads the real dataset.csv, cleans it, derives the two explainability ratios,
and writes ONE stratified, anonymised sample of REAL borrowers as a JS asset:

  data/borrowers.js   -> window.BORROWERS = [ {id, features, true_label}, ... ]
  data/meta.json      -> headline counts for the page

The page loads borrowers.js via <script src> (works on file:// and GitHub Pages).
The true_label is included but is used ONLY to score predictions AFTER the model
has answered. The browser never passes true_label into the classification prompt.

No API key needed - this is pure pandas sampling/cleaning.
"""
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
SRC = HERE / "dataset.csv"
OUT = HERE / "data"
OUT.mkdir(exist_ok=True)

SEED = 42
SAMPLE_N = 150  # the page lets the user classify 50 / 100 / all of these live


def parse_amount(val):
    """'£35,000.00' -> 35000.0 ; handles blanks."""
    if pd.isna(val):
        return None
    s = re.sub(r"[^0-9.]", "", str(val))
    return float(s) if s else None


def prior_default(val):
    if pd.isna(val) or str(val).strip() == "":
        return "unknown"
    v = str(val).strip().upper()
    if v == "Y":
        return "yes"
    if v == "N":
        return "no"
    return "unknown"


def main():
    df = pd.read_csv(SRC)
    print(f"Loaded {len(df):,} rows x {df.shape[1]} cols")

    # --- label: drop unlabelled rows ---
    df = df[df["Current_loan_status"].isin(["DEFAULT", "NO DEFAULT"])].copy()
    print(f"After dropping unlabelled: {len(df):,} rows")

    # --- parse currency amount, coerce numeric cols, drop rows missing essentials ---
    df["loan_amount"] = df["loan_amnt"].apply(parse_amount)
    num_cols = [
        "customer_age",
        "customer_income",
        "employment_duration",
        "loan_int_rate",
        "term_years",
        "cred_hist_length",
    ]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["loan_amount", "customer_income", "customer_age"]).copy()

    # --- impute: interest rate by grade median, employment by overall median ---
    df["loan_int_rate"] = df.groupby("loan_grade")["loan_int_rate"].transform(
        lambda s: s.fillna(s.median())
    )
    df["loan_int_rate"] = df["loan_int_rate"].fillna(df["loan_int_rate"].median())
    df["employment_duration"] = df["employment_duration"].fillna(
        df["employment_duration"].median()
    )

    # --- derived features (the explainability signals) ---
    df["loan_to_income_pct"] = (df["loan_amount"] / df["customer_income"] * 100).round(1)
    grade_med_rate = df.groupby("loan_grade")["loan_int_rate"].transform("median")
    df["rate_above_grade_norm"] = (df["loan_int_rate"] - grade_med_rate).round(2)

    df["prior_default"] = df["historical_default"].apply(prior_default)

    default_rate = (df["Current_loan_status"] == "DEFAULT").mean()
    print(f"Usable rows: {len(df):,} | DEFAULT rate: {default_rate:.1%}")

    def to_record(row, idx):
        return {
            "id": f"B{idx:04d}",
            "features": {
                "age": int(row["customer_age"]),
                "income": int(row["customer_income"]),
                "home_ownership": row["home_ownership"],
                "employment_duration": int(row["employment_duration"]),
                "loan_intent": row["loan_intent"],
                "loan_grade": row["loan_grade"],
                "loan_amount": int(row["loan_amount"]),
                "interest_rate": round(float(row["loan_int_rate"]), 2),
                "term_years": int(row["term_years"]),
                "prior_default": row["prior_default"],
                "credit_history_length": int(row["cred_hist_length"]),
                "loan_to_income_pct": float(row["loan_to_income_pct"]),
                "rate_above_grade_norm": float(row["rate_above_grade_norm"]),
            },
            "true_label": row["Current_loan_status"],
        }

    # --- one stratified sample, preserving the real ~21% default rate ---
    def stratified(frame, n, seed):
        frac_default = (frame["Current_loan_status"] == "DEFAULT").mean()
        n_def = max(1, round(n * frac_default))
        n_nod = n - n_def
        d = frame[frame["Current_loan_status"] == "DEFAULT"].sample(
            n_def, random_state=seed
        )
        nd = frame[frame["Current_loan_status"] == "NO DEFAULT"].sample(
            n_nod, random_state=seed
        )
        return pd.concat([d, nd]).sample(frac=1, random_state=seed)  # shuffle

    sample = stratified(df, SAMPLE_N, SEED)
    records = [to_record(r, i + 1) for i, (_, r) in enumerate(sample.iterrows())]

    n_def = sum(r["true_label"] == "DEFAULT" for r in records)
    meta = {
        "total_usable_rows": int(len(df)),
        "overall_default_rate_pct": round(default_rate * 100, 1),
        "sample_count": len(records),
        "sample_default_count": n_def,
        "sample_no_default_count": len(records) - n_def,
    }

    # JS asset loaded via <script src> - self-contained, no fetch/CORS needed
    js = (
        "/* Auto-generated by prep_data.py from the real dataset.csv. */\n"
        "/* Real held-out borrowers; true_label is scored ONLY after the model answers. */\n"
        "window.BORROWERS = "
        + json.dumps(records, indent=0).replace("\n", "")
        + ";\n"
        "window.BORROWERS_META = "
        + json.dumps(meta)
        + ";\n"
    )
    (OUT / "borrowers.js").write_text(js, encoding="utf-8")
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Wrote data/borrowers.js ({len(records)} real borrowers)")
    print(f"Sample default mix: {n_def} DEFAULT / {len(records) - n_def} NO DEFAULT")


if __name__ == "__main__":
    main()
