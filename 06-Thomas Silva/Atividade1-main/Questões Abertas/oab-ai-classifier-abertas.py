# Codigo pegando de 3 IA funcionando Questões ABERTAS
!pip install groq
!pip install fpdf
!pip install fpdf

from groq import Groq

import pandas as pd
import time
from groq import Groq
from huggingface_hub import InferenceClient
from datasets import load_dataset
from fpdf import FPDF

# ==========================================================
# CONFIGURAÇÃO (Thomas: Lote 11 a 20)
# ==========================================================
CHAVE_GROQ = "SUA-CHAVE"
CHAVE_HF   = "SUA CHAVE"

INICIO_LOTE, FIM_LOTE = 10, 20
# ==========================================================

client_groq = Groq(api_key=CHAVE_GROQ)
client_hf   = InferenceClient(api_key=CHAVE_HF)

print("Iniciando processamento final (Lote 11-20)...")
dataset = load_dataset("maritaca-ai/oab-bench", "questions", split="train")
meu_lote = dataset.select(range(INICIO_LOTE, FIM_LOTE))

resultados = []
for i, item in enumerate(meu_lote):
    pergunta = item['statement']
    id_real = INICIO_LOTE + i + 1
    print(f"Processando Questao {id_real}...")

    # IA 1: Meta - LLAMA 3.3 70B (Via Groq - Seu modelo mais forte)
    try:
        res1 = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": pergunta}],
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
    except Exception as e: res1 = f"Erro Llama 70B: {str(e)[:30]}"

    # IA 2: Meta - LLAMA 3.1 8B (Via Groq - Modelo leve que nao gera erro 400)
    try:
        res2 = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": pergunta}],
            model="llama-3.1-8b-instant"
        ).choices[0].message.content
    except Exception as e: res2 = f"Erro Llama 8B: {str(e)[:30]}"

    # IA 3: Alibaba - QWEN 2.5 (Via Hugging Face - Estavel)
    try:
        res3 = client_hf.chat_completion(
            messages=[{"role": "user", "content": pergunta}],
            model="Qwen/Qwen2.5-7B-Instruct",
            max_tokens=600
        ).choices[0].message.content
    except Exception as e: res3 = f"Erro Qwen: {str(e)[:30]}"

    resultados.append({"id": id_real, "p": pergunta, "r1": res1, "r2": res2, "r3": res3})
    time.sleep(1)

# GERAÇÃO DO PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Relatorio Thomas - Lote 11-20 (Versao Estabilidade Total)', 0, 1, 'C')

def limpar(txt): return str(txt).encode('latin-1', 'ignore').decode('latin-1')

pdf = PDF(); pdf.add_page()
for res in resultados:
    pdf.set_font('Arial', 'B', 10); pdf.multi_cell(0, 8, f"Questao {res['id']}:", 1)
    pdf.set_font('Arial', '', 9); pdf.multi_cell(0, 6, limpar(res['p']))

    for nome, texto in [("IA1 - LLAMA 70B", res['r1']), ("IA2 - LLAMA 8B", res['r2']), ("IA3 - QWEN 2.5", res['r3'])]:
        pdf.set_font('Arial', 'B', 9); pdf.cell(0, 7, f"-> {nome}:", 0, 1)
        pdf.set_font('Arial', '', 8); pdf.multi_cell(0, 5, limpar(texto))
    pdf.ln(5)

pdf.output("Relatorio_Thomas_Lote_11_20.pdf")
print("\n=== SUCESSO! PDF GERADO: Relatorio_Thomas_Lote_Final_Sempre.pdf ===")
