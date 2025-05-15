
# 💸 Fillcash Pipeline

Este projeto executa um pipeline de processamento de extratos bancários com os seguintes passos:

1. **Extração** dos dados brutos de extratos bancários (PDF ou CSV)
2. **Geração** do fluxo de caixa consolidado (`silver_statements.csv`)
3. **Projeção** de faturas futuras de cartões de crédito
4. **Formatação** da planilha em Excel com regras visuais e fórmulas financeiras (`format_sheet_*.xlsx`)

---

## 🧠 Como funciona

Você executa o pipeline com:

```bash
python run_pipeline.py
```

Isso irá:

1. Ler o arquivo `config.yml`
2. Identificar o banco e o tipo de extrato
3. Rodar a extração correspondente
4. Gerar `outputs/silver_statements.csv` com fluxo de caixa consolidado
5. Usar faturas de cartões previstas em `statements/future_card_bills.xlsx`
6. Gerar `outputs/format_sheet_<data>.xlsx` com regras visuais, saldos e descontos de fatura

---

## 📁 Estrutura esperada

```
config.yml
statements/
├── <banco>/file.<extensão>
├── future_card_bills.xlsx      ← (gerado automaticamente)
outputs/
├── silver_statements.csv
├── format_sheet_<data>.xlsx
src/
├── run_pipeline.py
├── extractors.py
├── formatter.py
├── generate_future_card_bills.py
```

---

## 🛠️ `config.yml`

```yaml
bankname: itau            # ou 'bradesco' ou 'c6'
statement_format: pdf     # 'pdf' (somente Itaú) ou 'csv'
cards:
  - bank: nubank
    name: pessoal
    last_digits: "1234"
    due_day: 10
    amount: 800.00
    color: ["#000000", "#eeeeee", "#dddddd"]
```

### Parâmetros suportados:

| Parâmetro           | Tipo     | Descrição                                                                 |
|---------------------|----------|---------------------------------------------------------------------------|
| `bankname`          | string   | Nome do banco: `itau`, `bradesco` ou `c6`                                 |
| `statement_format`  | string   | Formato do extrato: `pdf` (somente Itaú) ou `csv` (Bradesco, C6)          |
| `cards`             | lista    | Lista de cartões para projeções e visualizações                           |

---

## ✅ Bancos Suportados

| Banco     | Formato de entrada | Suporte |
|-----------|--------------------|---------|
| Itaú      | PDF                | ✅      |
| Bradesco  | CSV                | ✅      |
| C6 Bank   | CSV                | ✅      |

*Outros bancos e formatos serão adicionados futuramente.*

---

## 📦 Saídas geradas

- `outputs/current_account_statement.csv`: extrato padronizado
- `outputs/silver_statements.csv`: fluxo de caixa consolidado com projeções
- `outputs/format_sheet_<data>.xlsx`: planilha Excel final formatada
- `statements/future_card_bills.xlsx`: faturas mensais por cartão

---

## 📅 Projeção de faturas de cartões

O script `generate_future_card_bills.py` gera uma planilha com 12 meses de faturas futuras para cada cartão listado no `config.yml`.

Cada linha contém:

- `bank`, `name`, `last_digits` — identificação do cartão
- `due_day` — dia de vencimento
- `month`, `due_date` — data estimada da fatura
- `amount` — valor fixo estimado da fatura

Esses valores são aplicados automaticamente na planilha de fluxo de caixa no dia correspondente.

---

## 🧩 Extensibilidade

Para adicionar um novo banco:

1. Crie `def extract_novobanco(self)` em `extractors.py`
2. Nomeie a pasta `statements/novobanco/`
3. Atualize `config.yml` com:
```yaml
bankname: novobanco
statement_format: csv
```

---

## 🔧 Requisitos

- Python 3.8+
- Bibliotecas:
  - `pandas`
  - `openpyxl`
  - `pdfplumber`
  - `pyyaml`

---

## 🧪 Autor

Otavio Clark · `fillcash`

