
"""
extract_fillcash_csv_itau.py

Reads a PDF bank statement from Itaú and generates a cleaned CSV file
(removed 'SALDO DO DIA' lines) with inflow/outflow summary and full transactions.

Input:  statements/itau/itau_extrato_012025.pdf
Output: outputs/current_account_statement.csv
"""

import pdfplumber
import pandas as pd
from datetime import datetime
from pathlib import Path

def extract_transactions(pdf_path):
    transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split('\n')
            for line in lines:
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                try:
                    date = datetime.strptime(parts[0], "%d/%m/%Y").date()
                    amount_str = parts[-1]
                    amount = float(amount_str.replace('.', '').replace(',', '.'))
                    description = " ".join(parts[1:-1])
                    transactions.append({
                        "date": date,
                        "description": description.strip(),
                        "amount": amount
                    })
                except Exception:
                    continue

    df = pd.DataFrame(transactions)
    df = df[~df["description"].str.contains("SALDO DO DIA", case=False, na=False)]
    df["inflow"] = df["amount"].apply(lambda x: x if x > 0 else 0)
    df["outflow"] = df["amount"].apply(lambda x: -x if x < 0 else 0)

    return df

if __name__ == "__main__":
    base_folder = Path("statements/itau")
    file_name = "file.pdf"
    pdf_path = base_folder / file_name

    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
    else:
        df = extract_transactions(pdf_path)
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "current_account_statement.csv"
        df.to_csv(output_path, sep="|", index=False)
        print(f"✅ Exported to {output_path}")
