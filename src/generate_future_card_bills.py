
from datetime import datetime
import pandas as pd
import yaml
from pathlib import Path

def generate_future_card_bills():
    config_path = Path("config.yml")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    cards = config.get("cards", [])
    today = datetime.today()
    future_months = pd.date_range(start=today, periods=12, freq="MS").to_pydatetime()

    rows = []
    for card in cards:
        for month in future_months:
            rows.append({
                "bank": card["bank"],
                "name": card["name"],
                "last_digits": card["last_digits"],
                "due_day": card["due_day"],
                "month": month.strftime("%Y-%m"),
                "due_date": datetime(month.year, month.month, card["due_day"]),
                "amount": 0.0
            })

    df = pd.DataFrame(rows)
    output_path = Path("statements/future_card_bills.xlsx")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"✅ future_card_bills.xlsx salvo em: {output_path}")

if __name__ == "__main__":
    generate_future_card_bills()
