# Resposta das questões Abertas 107 - 212
# 1. Instalação das bibliotecas necessárias
# !pip install -q reportlab pandas groq datasets

import pandas as pd
import time, json
from datasets import load_dataset
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# 2. Configuração
CHAVE_GROQ = "SUA CHAVE"
client = Groq(api_key=CHAVE_GROQ)

# 3. Carregamento do Lote Thomas (107 a 212)
dataset_j2 = load_dataset("eduagarcia/oab_exams", split="train")
lote_thomas = dataset_j2.select(range(106, 212))

# 4. Função de Curadoria e Resposta (Incerência)
def processar_questao(enunciado, alternativas):
    prompt = f"""
    Atue como um Especialista Jurídico. Analise a questão da OAB abaixo:
    
    QUESTÃO: {enunciado}
    ALTERNATIVAS: {alternativas}
    
    TAREFAS:
    1. Responda a questão escolhendo a letra correta (A, B, C ou D).
    2. Classifique a Área entre [Direito Constitucional, Direito Penal, Direito Administrativo, Direito do Trabalho, Direito Digital].
    3. Defina o Nível entre [Estagiário, Advogado, Ministro].
    4. Identifique a Referência Legal (Artigo/Lei).

    RESPONDA APENAS EM JSON:
    {{
      "resposta_ia": "LETRA",
      "area": "NOME_DA_AREA",
      "nivel": "NOME_DO_NIVEL",
      "referencia": "ARTIGO_OU_LEI"
    }}
    """
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        return json.loads(chat.choices[0].message.content)
    except:
        return {"resposta_ia": "Erro", "area": "Erro", "nivel": "Erro", "referencia": "Erro"}

# 5. Execução do Lote
resultados_finais = []
print(f"Iniciando Processamento de {len(lote_thomas)} questões...")

for i, row in enumerate(lote_thomas):
    txt_alts = " | ".join(row['choices']['text'])
    resIA = processar_questao(row['question'], txt_alts)
    
    # Validação do Acerto (LLM-Judge)
    status = "CORRETO" if resIA.get("resposta_ia") == row['answerKey'] else "INCORRETO"
    
    resultados_finais.append({
        "ID": 107 + i,
        "Enunciado": row['question'],
        "Área": resIA.get("area"),
        "Nível": resIA.get("nivel"),
        "Referência_Legal": resIA.get("referencia"),
        "Resposta_IA": resIA.get("resposta_ia"),
        "Gabarito_Oficial": row['answerKey'],
        "Validacao": status
    })
    
    if (i+1) % 5 == 0: print(f"Processadas {i+1} questões...")
    time.sleep(0.3)

df_final = pd.DataFrame(resultados_finais)

# 6. Geração do XML (Estrutura para o sistema)
df_final.to_xml("curadoria_thomas.xml", index=False, root_name="LoteThomas", row_name="Questao")

# 7. Geração do Relatório PDF (ReportLab - Sem Cortes)
def gerar_pdf(df, nome_pdf):
    doc = SimpleDocTemplate(nome_pdf, pagesize=A4, margin=15*mm)
    estilos = getSampleStyleSheet()
    elementos = []
    
    est_h = ParagraphStyle('H', fontSize=14, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=10)
    est_b = ParagraphStyle('B', fontSize=9, leading=11)
    
    elementos.append(Paragraph("Relatório de Performance e Curadoria IA", est_h))
    
    for _, row in df.iterrows():
        cor_status = colors.darkgreen if row['Validacao'] == "CORRETO" else colors.red
        
        data = [
            [Paragraph(f"<b>Questão {row['ID']} - {row['Área']}</b>", ParagraphStyle('T', textColor=colors.white))],
            [Paragraph(f"<b>Nível:</b> {row['Nível']}", est_b)],
            [Paragraph(f"<b>Enunciado:</b> {row['Enunciado'][:250]}...", est_b)],
            [Paragraph(f"<b>IA:</b> {row['Resposta_IA']} | <b>Gabarito:</b> {row['Gabarito_Oficial']} | <b>Status:</b> <font color='{cor_status.hexval()}'>{row['Validacao']}</font>", est_b)],
            [Paragraph(f"<b>Base Legal:</b> {row['Referência_Legal']}", est_b)]
        ]
        
        t = Table(data, colWidths=[180*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.Color(0.2,0.2,0.2)),
            ('BACKGROUND', (0,1), (0,4), colors.Color(0.95,0.95,0.95)),
            ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        elementos.append(t)
        elementos.append(Spacer(1, 6*mm))
    
    doc.build(elementos)

gerar_pdf(df_final, "Relatorio_Thomas_Final_Completo.pdf")
print("Processo concluído! XML e PDF gerados.")
