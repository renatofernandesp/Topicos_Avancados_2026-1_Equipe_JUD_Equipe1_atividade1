import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

AZUL_ESCURO  = colors.HexColor("#0f2b5b")
AZUL_MEDIO   = colors.HexColor("#1a4a8a")
AZUL_CLARO   = colors.HexColor("#0066cc")
CINZA_CLARO  = colors.HexColor("#f8f9fa")
CINZA_TEXTO  = colors.HexColor("#6c757d")
VERDE        = colors.HexColor("#28a745")
AMARELO      = colors.HexColor("#ffc107")
VERMELHO     = colors.HexColor("#dc3545")

NIVEL_CORES_PDF = {1: VERDE, 2: AZUL_CLARO, 3: AMARELO, 4: VERMELHO}

NIVEL_LABELS = {
    1: "Nível 1 · Estagiário",
    2: "Nível 2 · Analista",
    3: "Nível 3 · Juiz de Direito",
    4: "Nível 4 · Ministro STF/STJ"
}

def _estilos():
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle("titulo", fontSize=20, textColor=colors.white,
                                  fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4),
        "subtitulo": ParagraphStyle("subtitulo", fontSize=10, textColor=colors.HexColor("#a8c4e8"),
                                     fontName="Helvetica", alignment=TA_CENTER),
        "secao": ParagraphStyle("secao", fontSize=12, textColor=AZUL_ESCURO,
                                 fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6),
        "corpo": ParagraphStyle("corpo", fontSize=9, textColor=colors.HexColor("#333333"),
                                 fontName="Helvetica", leading=13, spaceAfter=4),
        "label": ParagraphStyle("label", fontSize=8, textColor=CINZA_TEXTO,
                                 fontName="Helvetica", spaceAfter=2),
        "rodape": ParagraphStyle("rodape", fontSize=8, textColor=CINZA_TEXTO,
                                  fontName="Helvetica", alignment=TA_CENTER),
    }

def gerar_pdf(total, nivel_map, dados_area, pares, analises, niveis_dict, titulo_relatorio="Geral", nome_dataset=None) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=2*cm
    )
    s = _estilos()
    story = []
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── Cabeçalho ────────────────────────────────────────────────────────────
    if nome_dataset:
        subtitle_text = f"Modelo: {titulo_relatorio} | Dataset: {nome_dataset} | Gerado em {agora}"
    else:
        subtitle_text = f"Modelo: {titulo_relatorio} | Gerado em {agora}"
        
    header_data = [[Paragraph("⚖️  Relatório — Analisador Jurídico IA", s["titulo"])],
                   [Paragraph(subtitle_text, s["subtitulo"])]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AZUL_ESCURO),
        ("ROUNDEDCORNERS", [8]),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5*cm))

    # ── KPIs ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("Resumo Geral", s["secao"]))
    nivel_dominante = max(nivel_map, key=nivel_map.get) if nivel_map else 1
    kpi_data = [
        ["Total Analisado", "Áreas Identificadas", "Nível Predominante"],
        [str(total), str(len(dados_area)), f"N{nivel_dominante} · {niveis_dict.get(nivel_dominante, '')}"],
    ]
    kpi_table = Table(kpi_data, colWidths=[5.6*cm, 5.6*cm, 5.6*cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), AZUL_MEDIO),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9),
        ("BACKGROUND",   (0, 1), (-1, 1), CINZA_CLARO),
        ("FONTNAME",     (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 1), (-1, 1), 14),
        ("TEXTCOLOR",    (0, 1), (-1, 1), AZUL_ESCURO),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Distribuição por nível ────────────────────────────────────────────────
    story.append(Paragraph("Distribuição por Nível de Parecer", s["secao"]))
    nivel_rows = [["Nível", "Responsável", "Qtd", "%"]]
    for n in [1, 2, 3, 4]:
        qtd = nivel_map.get(n, 0)
        desc = niveis_dict.get(n, "")
        pct = f"{qtd/total*100:.1f}%" if total else "0%"
        nivel_rows.append([f"Nível {n}", desc, str(qtd), pct])

    nivel_table = Table(nivel_rows, colWidths=[3*cm, 7*cm, 3*cm, 4*cm])
    nivel_style = [
        ("BACKGROUND",    (0, 0), (-1, 0), AZUL_MEDIO),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ALIGN",         (2, 0), (-1, -1), "CENTER"),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, CINZA_CLARO]),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    for i, n in enumerate([1, 2, 3, 4], start=1):
        cor = NIVEL_CORES_PDF.get(n, AZUL_CLARO)
        nivel_style.append(("TEXTCOLOR", (0, i), (0, i), cor))
        nivel_style.append(("FONTNAME",  (0, i), (0, i), "Helvetica-Bold"))
    nivel_table.setStyle(TableStyle(nivel_style))
    story.append(nivel_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Distribuição por área ─────────────────────────────────────────────────
    story.append(Paragraph("Distribuição por Área Jurídica", s["secao"]))
    area_rows = [["Área", "Qtd", "%"]]
    for area, qtd in dados_area:
        area_fmt = area.replace("_", " ").title()
        pct = f"{qtd/total*100:.1f}%" if total else "0%"
        area_rows.append([area_fmt, str(qtd), pct])
    area_table = Table(area_rows, colWidths=[10*cm, 3.5*cm, 3.5*cm])
    area_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), AZUL_MEDIO),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, CINZA_CLARO]),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(area_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Métricas de qualidade ─────────────────────────────────────────────────
    if pares:
        import nltk
        from nltk.translate import meteor_score
        from nltk.tokenize import word_tokenize
        import random
        from analyzer import avaliar_com_llm_judge

        meteor_scores, cob_scores = [], []
        
        amostra_pares = random.sample(pares, min(5, len(pares)))
        llm_scores = []
        
        for texto, justificativa, base_legal in pares:
            try:
                ref_tokens = word_tokenize(texto)
                hyp_tokens = word_tokenize(justificativa)
                m_score = meteor_score.meteor_score([ref_tokens], hyp_tokens)
            except Exception:
                m_score = 0
            meteor_scores.append(m_score)
            
            if base_legal:
                termos = [t.strip().lower() for t in base_legal.split(",") if t.strip()]
                enc = sum(1 for t in termos if t in texto.lower())
                cob_scores.append(enc / len(termos) if termos else 0)
            else:
                cob_scores.append(0)

        for texto, justificativa, base_legal in amostra_pares:
             score = avaliar_com_llm_judge(texto, justificativa)
             llm_scores.append(score)

        m_med = sum(meteor_scores) / len(meteor_scores) if meteor_scores else 0
        llm_med = sum(llm_scores)  / len(llm_scores) if llm_scores else 0
        cob = sum(cob_scores) / len(cob_scores) if cob_scores else 0

        story.append(Paragraph("Métricas de Qualidade da IA", s["secao"]))
        met_rows = [
            ["Métrica", "Score", "Descrição"],
            ["METEOR", f"{m_med:.3f}", "Correspondência semântica e sinônimos das justificativas"],
            ["LLM-Judge (Amostra)", f"{llm_med:.3f}", "Fidedignidade factual avaliada por Inteligência Artificial"],
            ["Cobertura Base Legal", f"{cob:.1%}", "% de normas identificadas presentes no texto original"],
        ]
        met_table = Table(met_rows, colWidths=[4.5*cm, 3*cm, 9.5*cm])
        met_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), AZUL_MEDIO),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ALIGN",         (1, 0), (1, -1), "CENTER"),
            ("FONTNAME",      (1, 1), (1, -1), "Helvetica-Bold"),
            ("TEXTCOLOR",     (1, 1), (1, -1), AZUL_CLARO),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, CINZA_CLARO]),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(met_table)
        story.append(Spacer(1, 0.4*cm))

    # ── Detalhamento das análises ─────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=AZUL_MEDIO))
    story.append(Paragraph("Detalhamento das Análises", s["secao"]))

    for row in analises[:50]:  # limita a 50 para não gerar PDF gigante
        id_, texto, nivel, desc_nivel, area, base_legal, justificativa, modelo, fonte, criado_em = row
        area_fmt  = (area or "").replace("_", " ").title()
        cor_nivel = NIVEL_CORES_PDF.get(nivel, AZUL_CLARO)

        bloco = [
            Table([[
                Paragraph(f"#{id_}  ·  {NIVEL_LABELS.get(nivel, '')}  ·  {area_fmt}", ParagraphStyle(
                    "h", fontSize=9, fontName="Helvetica-Bold", textColor=colors.white)),
                Paragraph(criado_em[:16], ParagraphStyle(
                    "d", fontSize=8, fontName="Helvetica", textColor=colors.HexColor("#a8c4e8"),
                    alignment=2))
            ]], colWidths=[12*cm, 5*cm],
            style=TableStyle([
                ("BACKGROUND",   (0,0),(-1,-1), cor_nivel),
                ("TOPPADDING",   (0,0),(-1,-1), 7),
                ("BOTTOMPADDING",(0,0),(-1,-1), 7),
                ("LEFTPADDING",  (0,0),(-1,-1), 10),
                ("RIGHTPADDING", (0,0),(-1,-1), 10),
            ])),
            Table([[
                Table([
                    [Paragraph("Texto", s["label"])],
                    [Paragraph(texto[:400] + ("..." if len(texto) > 400 else ""), s["corpo"])],
                    [Paragraph("Base Legal", s["label"])],
                    [Paragraph(base_legal or "Não identificada", s["corpo"])],
                    [Paragraph("Justificativa IA", s["label"])],
                    [Paragraph(justificativa or "—", s["corpo"])],
                ], colWidths=[17*cm],
                style=TableStyle([
                    ("TOPPADDING",   (0,0),(-1,-1), 3),
                    ("BOTTOMPADDING",(0,0),(-1,-1), 3),
                    ("LEFTPADDING",  (0,0),(-1,-1), 0),
                    ("RIGHTPADDING", (0,0),(-1,-1), 0),
                ]))
            ]], colWidths=[17*cm],
            style=TableStyle([
                ("BACKGROUND",   (0,0),(-1,-1), CINZA_CLARO),
                ("TOPPADDING",   (0,0),(-1,-1), 8),
                ("BOTTOMPADDING",(0,0),(-1,-1), 8),
                ("LEFTPADDING",  (0,0),(-1,-1), 10),
                ("RIGHTPADDING", (0,0),(-1,-1), 10),
                ("LINEBELOW",    (0,0),(-1,-1), 0.5, colors.HexColor("#dee2e6")),
            ])),
        ]
        story.append(KeepTogether(bloco))
        story.append(Spacer(1, 0.2*cm))

    if len(analises) > 50:
        story.append(Paragraph(
            f"... e mais {len(analises) - 50} análises não exibidas. Exporte o CSV para o conjunto completo.",
            s["label"]
        ))

    # ── Rodapé ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CINZA_TEXTO))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Analisador Jurídico IA  ·  Gerado em {agora}  ·  {total} registros analisados",
        s["rodape"]
    ))

    doc.build(story)
    return buffer.getvalue()
