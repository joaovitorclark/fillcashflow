
"""
build_cashflow_data.py

Reads a cleaned transaction file and config.yml, applies fixed inflows and outflows,
and generates a daily-level cash flow CSV file.

Input: outputs/current_account_statement.csv
Output: outputs/silver_statements.csv
"""

import pandas as pd
import yaml
from datetime import datetime
from pathlib import Path

def build_cashflow(statement_path="outputs/current_account_statement.csv", config_path="config.yml", output_path="outputs/silver_statements.csv"):
    today = datetime.today()
    start_date = datetime(today.year, 1, 1)
    end_date = datetime(today.year + 1, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date)

    df1 = pd.read_csv(statement_path, sep="|")
    df1["date"] = pd.to_datetime(df1["date"]).dt.date

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    cards = config.get("cards", [])
    fixed_income = config.get("fixed_income", [])
    fixed_expenses = config.get("fixed_expenses", [])

    df = pd.DataFrame({"date": date_range})
    df["inflow"] = 0.0
    df["outflow"] = 0.0

    for card in cards:
        col = f"{card['bank'].capitalize()} - {card['name'].capitalize()} ({card['last_digits']})"
        df[col] = 0.0

    df["date"] = pd.to_datetime(df["date"]).dt.date

    extrato_por_dia = df1.groupby("date")[["inflow", "outflow"]].sum().reset_index()
    extrato_por_dia["date"] = pd.to_datetime(extrato_por_dia["date"]).dt.date

    dias_com_extrato = set(df1["date"].unique())
    last_real_date = df1["date"].max()

    for income in fixed_income:
        df.loc[
            (df["date"].apply(lambda d: d.day == income["day"] and d > last_real_date and d not in dias_com_extrato)),
            "inflow"
        ] += income["amount"]

    for expense in fixed_expenses:
        df.loc[
            (df["date"].apply(lambda d: d.day == expense["day"] and d > last_real_date and d not in dias_com_extrato)),
            "outflow"
        ] += expense["amount"]

    df_merge = df.merge(extrato_por_dia, on="date", how="left", suffixes=("", "_real"))
    df_merge["inflow"] = df_merge["inflow_real"].combine_first(df_merge["inflow"])
    df_merge["outflow"] = df_merge["outflow_real"].combine_first(df_merge["outflow"])

    df_merge["inflow"] = df_merge.apply(
        lambda row: row["inflow"] if row["date"] > last_real_date or row["date"] in dias_com_extrato else 0,
        axis=1
    )
    df_merge["outflow"] = df_merge.apply(
        lambda row: row["outflow"] if row["date"] > last_real_date or row["date"] in dias_com_extrato else 0,
        axis=1
    )

    df_merge = df_merge.drop(columns=["inflow_real", "outflow_real"])
    ordered_columns = ["date", "inflow", "outflow"] + [
        col for col in df_merge.columns if col not in ["date", "inflow", "outflow"]
    ]
    df_final = df_merge[ordered_columns]
    Path(output_path).parent.mkdir(exist_ok=True)
    df_final.to_csv(output_path, sep="|", index=False)
    print(f"✅ Silver statement saved to: {output_path}")

if __name__ == "__main__":
    build_cashflow()
