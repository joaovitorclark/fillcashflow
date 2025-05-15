
from pathlib import Path
from extractors import FillcashExtractor
from formatter import FillcashFormatter

def main():
    config_path = Path("config.yml")
    
    print("=== 🏦 INICIANDO PIPELINE DE EXTRATO ===")
    
    # Etapa 1: Extração
    extractor = FillcashExtractor(config_path)
    extractor.run()

    # Etapa 2: Pós-processamento (build + format)
    formatter = FillcashFormatter()
    formatter.run()

    print("✅ Pipeline finalizado com sucesso.")

if __name__ == "__main__":
    main()
