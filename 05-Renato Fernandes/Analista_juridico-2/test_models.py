import json
import os
from dotenv import load_dotenv

# Carrega .env explicitamente antes de importar analyzer
load_dotenv(dotenv_path=r"c:\Users\renperei\OneDrive - Capgemini\Desktop\Atividade1\.env")

from analyzer import MODELOS, analisar_texto

text = "O réu foi notificado e existe prazo de 5 dias para recurso; analise rapidamente."

for key in MODELOS:
    print('---', key)
    try:
        result = analisar_texto(text, key)
        print('OK:', json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print('ERRO:', type(e).__name__, str(e))
