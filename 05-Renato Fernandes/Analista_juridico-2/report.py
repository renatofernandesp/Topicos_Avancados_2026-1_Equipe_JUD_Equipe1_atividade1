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
ROXO         = colors.HexColor("#6f42c1")


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


def gerar_pdf(total, dados_area, pares, analises, titulo_relatorio="Geral", nome_dataset=None) -> bytes:
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

    # ── KPIs principais ───────────────────────────────────────────────────────
    story.append(Paragraph("Resumo Geral", s["secao"]))

    # Calcular métricas de MCQ
    mcq_analises = [a for a in analises
                    if a[10] is not None and str(a[10]).strip() not in ("", "None", "none")]
    corretas_count   = sum(1 for a in mcq_analises if a[13])
    incorretas_count = sum(1 for a in mcq_analises if not a[13])
    total_mcq        = corretas_count + incorretas_count
    pct_corretas     = f"{corretas_count/total_mcq*100:.1f}%" if total_mcq > 0 else "N/A"
    pct_incorretas   = f"{incorretas_count/total_mcq*100:.1f}%" if total_mcq > 0 else "N/A"

    if total_mcq > 0:
        kpi_headers = ["Total Analisado", "Áreas Identificadas", "% Corretas", "% Incorretas"]
        kpi_values  = [str(total), str(len(dados_area)), pct_corretas, pct_incorretas]
        col_w = [4.2*cm, 4.2*cm, 4.2*cm, 4.2*cm]
    else:
        kpi_headers = ["Total Analisado", "Áreas Identificadas"]
        kpi_values  = [str(total), str(len(dados_area))]
        col_w = [8.4*cm, 8.4*cm]

    kpi_data = [kpi_headers, kpi_values]
    kpi_table = Table(kpi_data, colWidths=col_w)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), AZUL_MEDIO),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9),
        ("BACKGROUND",   (0, 1), (-1, 1), CINZA_CLARO),
        ("FONTNAME",     (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 1), (-1, 1), 14),
        ("TEXTCOLOR",    (0, 1), (-1, 1), AZUL_ESCURO),
        ("TEXTCOLOR",    (2, 1), (2, 1), VERDE)   if total_mcq > 0 else ("TEXTCOLOR", (0,0),(0,0), AZUL_ESCURO),
        ("TEXTCOLOR",    (3, 1), (3, 1), VERMELHO) if total_mcq > 0 else ("TEXTCOLOR", (0,0),(0,0), AZUL_ESCURO),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Distribuição por Tipo de Questão ──────────────────────────────────────
    from database import contar_por_question_type
    dados_tipo = contar_por_question_type()
    if dados_tipo:
        story.append(Paragraph("Distribuição por Tipo de Questão", s["secao"]))
        tipo_rows = [["Tipo de Questão", "Qtd", "%"]]
        total_tipo = sum(t[1] for t in dados_tipo)
        for tipo, qtd in dados_tipo:
            tipo_fmt = (tipo or "").replace("_", " ").title()
            pct = f"{qtd/total_tipo*100:.1f}%" if total_tipo else "0%"
            tipo_rows.append([tipo_fmt, str(qtd), pct])
        tipo_table = Table(tipo_rows, colWidths=[10*cm, 3.5*cm, 3.5*cm])
        tipo_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), ROXO),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, CINZA_CLARO]),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(tipo_table)
        story.append(Spacer(1, 0.4*cm))




    # ── Métricas de qualidade ─────────────────────────────────────────────────
    if pares:
        import nltk
        from nltk.translate import meteor_score
        from nltk.tokenize import word_tokenize
        import random
        from analyzer import avaliar_com_llm_judge

        meteor_scores = []
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

        for texto, justificativa, base_legal in amostra_pares:
            score = avaliar_com_llm_judge(texto, justificativa)
            llm_scores.append(score)

        m_med   = sum(meteor_scores) / len(meteor_scores) if meteor_scores else 0
        llm_med = sum(llm_scores)    / len(llm_scores)    if llm_scores    else 0

        story.append(Paragraph("Métricas de Qualidade da IA", s["secao"]))
        met_rows = [
            ["Métrica", "Score", "Descrição"],
            ["METEOR",               f"{m_med:.1%}",   "Correspondência semântica e sinônimos das justificativas"],
            ["LLM-Judge (Amostra)",  f"{llm_med:.1%}", "Fidedignidade factual avaliada por Inteligência Artificial"],
        ]

        if total_mcq > 0:
            met_rows.append(["% Respostas Corretas",   pct_corretas,   f"{corretas_count} questões acertadas"])
            met_rows.append(["% Respostas Incorretas",  pct_incorretas, f"{incorretas_count} questões com gabarito diferente do modelo"])

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

    for row in analises:  # Iterate over all analyses without limit
        id_, texto, nivel, desc_nivel, area, base_legal, justificativa, modelo, fonte, criado_em, qid, gobj, gmod, gcor, qtype = row
        area_fmt = (area or "").replace("_", " ").title()
        qid = qid if (qid and str(qid).strip() and str(qid).lower() not in ("none", "")) else None

        # Linha de status do gabarito (apenas MCQ)
        status_gab = []
        if qid:
            if gcor:
                status_gab = [
                    Paragraph("Gabarito Oficial", s["label"]),
                    Paragraph(f"✅ CORRETO — Resposta Escolhida: {gobj} | Resposta do Modelo: {gmod}", s["corpo"]),
                ]
            else:
                status_gab = [
                    Paragraph("Gabarito Oficial", s["label"]),
                    Paragraph(f"❌ INCORRETO — Resposta Escolhida: {gobj} | Resposta Correta (modelo): {gmod}", s["corpo"]),
                ]

        inner_rows = [
            [Paragraph("Questão / Texto", s["label"])],
            [Paragraph(texto[:400] + ("..." if len(texto) > 400 else ""), s["corpo"])],
            [Paragraph("Justificativa IA", s["label"])],
            [Paragraph(justificativa or "—", s["corpo"])],
        ]
        if status_gab:
            inner_rows += [[item] for item in status_gab]

        bloco = [
            Table([[
                Paragraph(f"#{id_}  ·  {area_fmt}", ParagraphStyle(
                    "h", fontSize=9, fontName="Helvetica-Bold", textColor=colors.white)),
                Paragraph(criado_em[:16], ParagraphStyle(
                    "d", fontSize=8, fontName="Helvetica", textColor=colors.HexColor("#a8c4e8"),
                    alignment=2))
            ]], colWidths=[12*cm, 5*cm],
            style=TableStyle([
                ("BACKGROUND",   (0,0),(-1,-1), AZUL_CLARO),
                ("TOPPADDING",   (0,0),(-1,-1), 7),
                ("BOTTOMPADDING",(0,0),(-1,-1), 7),
                ("LEFTPADDING",  (0,0),(-1,-1), 10),
                ("RIGHTPADDING", (0,0),(-1,-1), 10),
            ])),
            Table([[
                Table(inner_rows, colWidths=[17*cm],
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

    # Limite removido, exibindo todas as análises no PDF

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
