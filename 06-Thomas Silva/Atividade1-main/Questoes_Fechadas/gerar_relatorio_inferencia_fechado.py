#Realização da inferencia das questões 107-216

# 1. Instalação das bibliotecas
!pip install -q reportlab pandas lxml

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# 2. Carregar a sua curadoria via XML
# Certifique-se que o arquivo 'curadoria_thomas.xml' está na pasta lateral do Colab
try:
    df = pd.read_xml('curadoria_thomas.xml')
    print("XML carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar XML: {e}. Certifique-se de que o arquivo existe.")

def gerar_relatorio_final_xml(dataframe, nome_arquivo):
    # Configuração do Documento
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4, 
                            rightMargin=15*mm, leftMargin=15*mm, 
                            topMargin=15*mm, bottomMargin=15*mm)
    
    estilos = getSampleStyleSheet()
    elementos = []

    # --- DEFINIÇÃO DE ESTILOS ---
    estilo_cabecalho = ParagraphStyle('Header', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=TA_CENTER, spaceAfter=10)
    estilo_sub_cabecalho = ParagraphStyle('SubHeader', parent=estilos['Normal'], fontName='Helvetica', fontSize=10, alignment=TA_CENTER, spaceAfter=20)
    estilo_titulo_card = ParagraphStyle('TituloCard', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white)
    estilo_texto = ParagraphStyle('TextoCard', fontName='Helvetica', fontSize=9, leading=11)
    estilo_status = ParagraphStyle('StatusCard', fontName='Helvetica-Bold', fontSize=10)

    # --- CABEÇALHO DO RELATÓRIO ---
    elementos.append(Paragraph("Relatório de Performance e Curadoria - Equipe 01", estilo_cabecalho))
    elementos.append(Paragraph("Curador: Thomas Araujo | Fonte: XML Judg", estilo_sub_cabecalho))

    # --- RESUMO ESTATÍSTICO (ACERTOS VS ERROS) ---
    if 'Validacao' in dataframe.columns:
        acertos = dataframe['Validacao'].value_counts().get('CORRETO', 0)
        total = len(dataframe)
        precisao = (acertos/total)*100 if total > 0 else 0
        
        elementos.append(Paragraph("<b>1. Resumo de Performance (LLM-Judge)</b>", estilos['Heading2']))
        elementos.append(Paragraph(f"Total de Questões: {total} | Acertos: {acertos} | Precisão: {precisao:.1f}%", estilos['Normal']))
        elementos.append(Spacer(1, 8*mm))

    # --- LOOP DAS QUESTÕES (CARDS) ---
    for i, row in dataframe.iterrows():
        # Limpeza e Segurança de Dados (Tratando possíveis campos vazios no XML)
        id_q = str(row.get('ID', 'N/A'))
        area = str(row.get('Área', row.get('area', 'Não Informado')))
        nivel = str(row.get('Nível', row.get('nivel', 'Não Informado')))
        enu = str(row.get('Enunciado', 'Sem conteúdo')).replace('\n', ' ').strip()
        ref = str(row.get('Referência_Legal', 'Sem referência')).replace('\n', ' ').strip()
        gab = str(row.get('Gabarito_Oficial', 'N/A'))
        resp_ia = str(row.get('Resposta_IA', 'N/A'))
        status = str(row.get('Validacao', 'N/A'))

        # Cor do Status
        cor_status = colors.darkgreen if status == "CORRETO" else colors.red

        # Estrutura do Card em Tabela
        data = [
            [Paragraph(f"Questão [{id_q}]: {area}", estilo_titulo_card)],
            [Paragraph(f"<b>Nível:</b> {nivel}", estilo_texto)],
            [Paragraph(f"<b>Enunciado:</b> {enu[:300]}...", estilo_texto)],
            [Paragraph(f"<b>IA:</b> {resp_ia} | <b>Gabarito:</b> {gab} | <b>Status:</b> <font color='{cor_status.hexval()}'>{status}</font>", estilo_texto)],
            [Paragraph(f"<b>Base Legal:</b> {ref}", estilo_texto)]
        ]

        t = Table(data, colWidths=[180*mm])
        
        # Cores Maverick
        cor_topo = colors.Color(50/255, 50/255, 50/255)
        cor_miolo = colors.Color(248/255, 248/255, 248/255)

        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), cor_topo),
            ('BACKGROUND', (0,1), (0,4), cor_miolo),
            ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 5),
        ]))

        elementos.append(t)
        elementos.append(Spacer(1, 6*mm))

    # Construção do PDF
    doc.build(elementos)
    print(f"Relatório gerado com sucesso a partir do XML: {nome_arquivo}")

# Execução
gerar_relatorio_final_xml(df, "Relatorio_Thomas_Final_XML.pdf")
