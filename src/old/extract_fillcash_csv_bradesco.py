import csv
import pandas as pd
from pathlib import Path
from datetime import datetime

def c6_csv_to_fillcash(input_csv: Path, output_csv: Path):
    transactions = []

    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header_found = False

        for row in reader:
            # Detecta a linha de cabeçalho
            if row and row[0].strip() == "Data Lançamento":
                header_found = True
                continue
            if not header_found:
                continue

            if len(row) < 7:
                continue  # ignora linhas incompletas

            date_raw = row[0].strip()
            description = row[3].strip()
            inflow_raw = row[4].strip().replace(',', '.')
            outflow_raw = row[5].strip().replace(',', '.')
            amount_raw = row[6].strip().replace(',', '.')

            try:
                date = datetime.strptime(date_raw, "%d/%m/%Y").strftime("%Y-%m-%d")
                inflow = float(inflow_raw) if inflow_raw else 0.0
                outflow = float(outflow_raw) if outflow_raw else 0.0
                amount = float(amount_raw) if amount_raw else 0.0
            except Exception:
                continue

            transactions.append({
                "date": date,
                "description": description,
                "amount": amount,
                "inflow": inflow,
                "outflow": outflow
            })

    df = pd.DataFrame(transactions)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, sep='|', index=False)
    print(f"✅ {len(df)} transações salvas em: {output_csv}")

if __name__ == "__main__":
    input_csv = Path("statements/c6/file.csv")
    output_csv = Path("outputs/current_account_statement.csv")
    c6_csv_to_fillcash(input_csv, output_csv)
