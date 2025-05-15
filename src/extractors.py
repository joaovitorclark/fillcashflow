
import pandas as pd
import csv
import pdfplumber
from datetime import datetime
from pathlib import Path
import yaml

class FillcashExtractor:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.bankname = config.get("bankname", "").lower()
        self.statement_format = config.get("statement_format", "csv").lower()
        self.input_path = Path(f"statements/{self.bankname}/file.{self.statement_format}")
        self.output_path = Path("outputs/current_account_statement.csv")

    def run(self):
        method_name = f"extract_{self.bankname}"
        method = getattr(self, method_name, None)
        if method is None:
            raise ValueError(f"Banco não suportado: {self.bankname}")
        print(f"▶️ Extraindo transações do banco {self.bankname} ({self.statement_format.upper()})")
        method()

    def extract_itau(self):
        if self.statement_format == "pdf":
            self.extract_itau_pdf()
        else:
            self.extract_itau_csv()

    def extract_itau_pdf(self):
        transactions = []
        with pdfplumber.open(self.input_path) as pdf:
            for page in pdf.pages:
                lines = page.extract_text().split('\n')
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 4:
                        continue
                    try:
                        date = datetime.strptime(parts[0], "%d/%m/%Y").strftime("%Y-%m-%d")
                        amount = float(parts[-1].replace('.', '').replace(',', '.'))
                        description = " ".join(parts[1:-1])
                        inflow = amount if amount > 0 else 0.0
                        outflow = -amount if amount < 0 else 0.0
                        transactions.append({
                            "date": date,
                            "description": description,
                            "amount": amount,
                            "inflow": inflow,
                            "outflow": outflow
                        })
                    except:
                        continue
        self.save_output(transactions)

    def extract_itau_csv(self):
        df = pd.read_csv(self.input_path, sep=";", encoding="utf-8", dtype=str)
        df = df.dropna(subset=["Data", "Histórico"])
        transactions = []
        for _, row in df.iterrows():
            try:
                date = pd.to_datetime(row["Data"], dayfirst=True).strftime("%Y-%m-%d")
                description = row["Histórico"].strip()
                amount = float(row["Valor"].replace('.', '').replace(',', '.'))
                inflow = amount if amount > 0 else 0.0
                outflow = -amount if amount < 0 else 0.0
                transactions.append({
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "inflow": inflow,
                    "outflow": outflow
                })
            except Exception:
                continue
        self.save_output(transactions)

    def extract_bradesco(self):
        transactions = []
        with open(self.input_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=";")
            header_found = False
            for row in reader:
                if not header_found and row[:6] == ["Data", "Histórico", "Docto.", "Crédito (R$)", "Débito (R$)", "Saldo (R$)"]:
                    header_found = True
                    continue
                if not header_found or len(row) < 6 or not row[0].strip():
                    continue
                try:
                    date = datetime.strptime(row[0].strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
                    description = row[1].strip()
                    inflow = float(row[3].replace('.', '').replace(',', '.')) if row[3].strip() else 0.0
                    outflow = float(row[4].replace('.', '').replace(',', '.')) if row[4].strip() else 0.0
                    amount = float(row[5].replace('.', '').replace(',', '.')) if row[5].strip() else 0.0
                    transactions.append({
                        "date": date,
                        "description": description,
                        "amount": amount,
                        "inflow": inflow,
                        "outflow": outflow
                    })
                except Exception:
                    continue
        self.save_output(transactions)

    def extract_c6(self):
        transactions = []
        with open(self.input_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header_found = False
            for row in reader:
                if row and row[0].strip() == "Data Lançamento":
                    header_found = True
                    continue
                if not header_found or len(row) < 7:
                    continue
                try:
                    date = datetime.strptime(row[0].strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
                    description = row[3].strip()
                    inflow = float(row[4].replace(',', '.')) if row[4].strip() else 0.0
                    outflow = float(row[5].replace(',', '.')) if row[5].strip() else 0.0
                    amount = float(row[6].replace(',', '.')) if row[6].strip() else 0.0
                    transactions.append({
                        "date": date,
                        "description": description,
                        "amount": amount,
                        "inflow": inflow,
                        "outflow": outflow
                    })
                except Exception:
                    continue
        self.save_output(transactions)

    def save_output(self, transactions):
        df = pd.DataFrame(transactions)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output_path, sep="|", index=False)
        print(f"✅ {len(df)} transações salvas em: {self.output_path}")
