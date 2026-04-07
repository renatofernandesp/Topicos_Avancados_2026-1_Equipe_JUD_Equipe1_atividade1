import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from database import init_db, inserir_analise, listar_analises, contar_por_area, salvar_dataset, listar_datasets, excluir_dataset, get_dataset_conteudo, listar_analises_com_justificativa, listar_modelos_usados, contar_por_question_type, limpar_analises
from report import gerar_pdf
from analyzer import analisar_lote, AREAS, MODELOS, avaliar_com_llm_judge
from parser import parse_arquivo

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Analisador Jurídico IA",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# ── Estilos ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .card {
        background: #f8f9fa;
        border-left: 4px solid #0066cc;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .stProgress > div > div { background-color: #0066cc; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/scales.png", width=60)
    st.title("⚖️ Analisador Jurídico")
    st.caption("Classificação inteligente de questões jurídicas via IA")
    st.divider()
    pagina = st.radio("Navegação", ["📤 Importar Dataset", "📊 Dashboard", "🔍 Consultar Análises"], label_visibility="collapsed")

# ── Página: Importar Dataset ─────────────────────────────────────────────────
if pagina == "📤 Importar Dataset":
    st.header("📤 Importar Dataset Jurídico")
    st.caption("Suporte a arquivos JSON, CSV e TXT")

    col1, col2 = st.columns([2, 1])
    with col1:
        arquivo = st.file_uploader(
            "Selecione o arquivo do dataset",
            type=["json", "csv", "txt", "xlsx"],
            help="JSON/CSV/TXT (texto livre) | XLSX (suporta também colunas: ID_Question, question_type, question, choices, answerKey)"
        )

    with col2:
        st.info("**Formatos aceitos:**\n- **JSON**: lista de objetos ou strings\n- **CSV**: qualquer estrutura tabular\n- **TXT**: parágrafos ou linhas")

    if arquivo:
        conteudo = arquivo.read()
        try:
            registros = parse_arquivo(conteudo, arquivo.name)

            # Ordena os registros em ordem cronológica baseada na coluna ID
            if registros and isinstance(registros[0], dict) and "ID_Question" in registros[0]:
                def sort_by_id(r):
                    id_val = str(r.get("ID_Question", ""))
                    digits = ''.join(filter(str.isdigit, id_val))
                    if digits:
                        return (0, int(digits))
                    return (1, id_val)
                registros.sort(key=sort_by_id)

            st.success(f"✅ **{len(registros)} registros** encontrados em `{arquivo.name}`")

            with st.expander("👁️ Pré-visualização dos registros", expanded=False):
                for i, r in enumerate(registros[:5]):
                    if isinstance(r, dict):
                        preview = (
                            f"**ID:** {r.get('ID_Question','')} | "
                            f"**Tipo:** {r.get('question_type','')} | "
                            f"**Questão:** {str(r.get('question',''))[:250]} | "
                            f"**Resposta Escolhida:** {r.get('answerKey','')}"
                        )
                    else:
                        preview = str(r)[:300] + ("..." if len(str(r)) > 300 else "")
                    st.markdown(f"<div class='card'><small><b>#{i+1}</b></small><br>{preview}</div>", unsafe_allow_html=True)
                if len(registros) > 5:
                    st.caption(f"... e mais {len(registros) - 5} registros")

            limite = st.slider("Quantidade de registros a analisar", 1, min(len(registros), 100), min(len(registros), 10))

            modelos_opcoes = {k: v["label"] for k, v in MODELOS.items()}
            modelos_selecionados = st.multiselect(
                "🤖 Modelos para análise",
                options=list(modelos_opcoes.keys()),
                default=["gpt-4o-mini"],
                format_func=lambda k: modelos_opcoes[k]
            )

            if st.button("🚀 Iniciar Análise com IA", type="primary", use_container_width=True, disabled=not modelos_selecionados):
                dataset_id = salvar_dataset(arquivo.name, conteudo, len(registros))

                progress_bar = st.progress(0)
                status_text = st.empty()

                def atualizar_progresso(atual, total):
                    progress_bar.progress(atual / total)
                    status_text.markdown(f"⏳ Analisando registro **{atual}** de **{total}**...")

                with st.spinner("Conectando ao Azure OpenAI..."):
                    resultados = analisar_lote(registros[:limite], arquivo.name, modelos_selecionados, atualizar_progresso)

                progress_bar.progress(1.0)
                status_text.success(f"✅ Análise concluída! {len(resultados)} registros processados.")

                sucessos = [r for r in resultados if r["area"] != "indefinido"]
                erros_list = [r for r in resultados if r["area"] == "indefinido"]

                if erros_list:
                    st.warning(f"⚠️ {len(erros_list)} registro(s) com erro durante a análise.")
                    with st.expander("👁️ Ver detalhes dos erros"):
                        for erro in erros_list:
                            modelo_label = MODELOS.get(erro.get("modelo"), {}).get("label", erro.get("modelo"))
                            error_message = erro.get('base_legal', 'Erro desconhecido.')
                            st.error(f"**Modelo:** {modelo_label}\n\n**Detalhes:** {error_message}", icon="🚨")

                if sucessos:
                    for r in sucessos:
                        inserir_analise(dataset_id, r["texto"], r["nivel"], r["descricao_nivel"], r["area"], r["base_legal"], r["justificativa"], r["modelo"], r["fonte"], r.get("questao_id"), r.get("gabarito_oficial"), r.get("gabarito_modelo"), r.get("gabarito_correto"), r.get("question_type"))
                    st.balloons()
                    st.info("💡 Acesse **Dashboard** ou **Consultar Análises** para ver os resultados.")

        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")

    # ── Datasets armazenados ─────────────────────────────────────────────────
    st.divider()
    st.subheader("📁 Datasets Armazenados")
    datasets = listar_datasets()
    if not datasets:
        st.info("Nenhum dataset importado ainda.")
    else:
        for ds in datasets:
            ds_id, ds_nome, ds_total, ds_data = ds
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.markdown(f"📄 **{ds_nome}** · {ds_total} registros · `{ds_data[:16]}`")
            with col_b:
                row = get_dataset_conteudo(ds_id)
                if row:
                    st.download_button("⬇️ Baixar", row[1], file_name=row[0], key=f"dl_{ds_id}", use_container_width=True)
            with col_c:
                if st.button("🗑️ Excluir", key=f"del_{ds_id}", use_container_width=True, type="secondary"):
                    excluir_dataset(ds_id)
                    st.success(f"Dataset `{ds_nome}` excluído.")
                    st.rerun()

    # Botão de limpeza de análises
    st.divider()
    with st.expander("⚠️ Limpar Análises (Reimportar)", expanded=False):
        st.warning("⚠️ Isso apaga **todas as análises** salvas, mas  **mantém** os datasets. Use quando quiser reimportar após mudanças no código.")
        if st.button("🗑️ Limpar todas as análises", type="primary", use_container_width=True, key="btn_limpar"):
            limpar_analises()
            st.success("✅ Análises limpas! Agora importe novamente o dataset acima.")
            st.rerun()

# ── Página: Dashboard ────────────────────────────────────────────────────────
elif pagina == "📊 Dashboard":

    modelos_usados = listar_modelos_usados()
    analises_banco = listar_analises()

    if not analises_banco:
        st.markdown("""<div style='display:flex;flex-direction:column;align-items:center;
            justify-content:center;height:60vh;gap:12px;'>
            <span style='font-size:3rem'>⚖️</span>
            <h3 style='color:#6c757d;margin:0'>Nenhuma análise encontrada</h3>
            <p style='color:#adb5bd;margin:0'>Importe um dataset na aba <b>Importar Dataset</b> para começar.</p>
            </div>""", unsafe_allow_html=True)
    else:
        abas_titulos = ["Visão Geral"] + [MODELOS.get(m, {}).get("label", m) for m in modelos_usados]
        modelos_keys = [None] + modelos_usados
        abas = st.tabs(abas_titulos)
        
        datasets   = listar_datasets()
        n_datasets = len(datasets)
        
        if n_datasets == 1:
            dataset_str = datasets[0][1]
        elif n_datasets > 1:
            dataset_str = f"Múltiplos ({n_datasets})"
        else:
            dataset_str = None

        for idx, modelo_ativo in enumerate(modelos_keys):
            with abas[idx]:
                dados_area  = contar_por_area(modelo_ativo)
                pares       = listar_analises_com_justificativa(modelo_ativo)
                todas_analises = listar_analises(filtro_modelo=modelo_ativo)
                total      = len(todas_analises)
                areas_unicas = len(dados_area)

                # MCQ stats — agora listar_analises retorna 15 colunas (inclui question_type no índice 14)
                COLS = ["ID","Texto","Nível","Desc","Área","BaseLegal","Justificativa",
                        "Modelo","Fonte","Data","QuestaoID","GabOficial","GabModelo","GabCorreto","QuestionType"]
                df_todas = pd.DataFrame(todas_analises, columns=COLS) if todas_analises else pd.DataFrame()
                # Uma questão é MCQ se tiver QuestaoID não-nulo e não-vazio
                if not df_todas.empty:
                    mcq_df = df_todas[df_todas["QuestaoID"].notnull() & (df_todas["QuestaoID"].astype(str).str.strip() != "") & (df_todas["QuestaoID"].astype(str).str.lower() != "none")]
                else:
                    mcq_df = pd.DataFrame()
                n_corretas   = int(mcq_df["GabCorreto"].fillna(0).sum()) if not mcq_df.empty else None
                n_incorretas = len(mcq_df) - n_corretas                   if n_corretas is not None else None

                # ── Cabeçalho com botão PDF ──────────────────────────────────────────
                col_header, col_btn = st.columns([3, 1])
                with col_header:
                    titulo_dash = "Visão Consolidada" if modelo_ativo is None else f"Análise: {MODELOS.get(modelo_ativo, {}).get('label', modelo_ativo)}"
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#0f2b5b 0%,#1a4a8a 100%);
                         border-radius:12px;padding:28px 32px;'>
                        <h2 style='color:#fff;margin:0;font-size:1.6rem'>⚖️ Dashboard Jurídico</h2>
                        <p style='color:#a8c4e8;margin:4px 0 0'>{titulo_dash}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
                    try:
                        if modelo_ativo is None:
                            if len(modelos_usados) == 1:
                                titulo_rel = MODELOS.get(modelos_usados[0], {}).get("label", modelos_usados[0])
                            else:
                                labels = [MODELOS.get(m, {}).get("label", m) for m in modelos_usados]
                                titulo_rel = "Todos os Modelos: " + " | ".join(labels)
                        else:
                            titulo_rel = MODELOS.get(modelo_ativo, {}).get("label", modelo_ativo)

                        pdf_bytes = gerar_pdf(
                            total=total, dados_area=dados_area,
                            pares=pares, analises=todas_analises,
                            titulo_relatorio=titulo_rel,
                            nome_dataset=dataset_str
                        )
                        sufixo = titulo_rel.replace(" ", "_").replace("|", "-")[:40]
                        st.download_button(
                            label="📄 Baixar Relatório PDF",
                            data=pdf_bytes,
                            file_name=f"relatorio_juridico_{sufixo}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary",
                            key=f"dl_pdf_{idx}"
                        )
                    except Exception as e:
                        st.error(f"Erro ao gerar PDF: {e}")


                st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

                if total == 0:
                    st.info("Não há dados processados para este modelo.")
                    continue

                # ── KPIs principais ──────────────────────────────────────────────────
                k1, k2, k3 = st.columns(3)
                kpi_style = lambda cor: f"""
                    background:{cor}15;border-left:4px solid {cor};
                    border-radius:8px;padding:16px 20px;
                """
                def kpi_card(col, icon, label, value, cor):
                    col.markdown(f"""
                    <div style='{kpi_style(cor)}'>
                        <div style='font-size:1.6rem'>{icon}</div>
                        <div style='font-size:1.8rem;font-weight:700;color:{cor};line-height:1.2'>{value}</div>
                        <div style='font-size:0.8rem;color:#6c757d;margin-top:2px'>{label}</div>
                    </div>""", unsafe_allow_html=True)

                kpi_card(k1, "📋", "Total Analisado",    total,        "#0066cc")
                kpi_card(k2, "📁", "Datasets Importados", n_datasets,  "#6f42c1")
                kpi_card(k3, "🏛️", "Áreas Identificadas", areas_unicas, "#fd7e14")

                # KPIs de MCQ (corretas/incorretas)
                if n_corretas is not None:
                    k4, k5 = st.columns(2)
                    kpi_card(k4, "✅", "Gabaritos Corretos",   n_corretas,   "#28a745")
                    kpi_card(k5, "❌", "Gabaritos Incorretos", n_incorretas, "#dc3545")

                st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

                # ── % Tipo de Questão (largura total) ─────────────────────────
                dados_tipo = contar_por_question_type(modelo_ativo)
                st.markdown("<p style='font-weight:600;font-size:1rem;margin-bottom:4px'>📂 Tipo de Questão</p>", unsafe_allow_html=True)
                if dados_tipo:
                    df_tipo = pd.DataFrame(dados_tipo, columns=["Tipo", "Total"])
                    df_tipo["Tipo"] = df_tipo["Tipo"].str.replace("_", " ").str.title()
                    fig_tipo = px.pie(
                        df_tipo, values="Total", names="Tipo",
                        hole=0.55,
                        color_discrete_sequence=px.colors.sequential.Purples_r
                    )
                    fig_tipo.update_traces(
                        textposition="outside", textinfo="label+percent",
                        pull=[0.03] * len(df_tipo)
                    )
                    fig_tipo.update_layout(
                        showlegend=True, margin=dict(t=20, b=20, l=0, r=0),
                        paper_bgcolor="rgba(0,0,0,0)", height=320
                    )
                    st.plotly_chart(fig_tipo, use_container_width=True, key=f"f_tipo_{idx}")
                else:
                    st.info("Sem dados de Tipo de Questão.")


                # ── Comparativo entre modelos (apenas na Visão Geral) ────────────────
                if modelo_ativo is None and len(modelos_usados) > 1:
                    st.divider()
                    st.markdown("<p style='font-weight:600;font-size:1.2rem;margin:12px 0 4px'>🤖 Acurácia Múltipla Escolha por Modelo</p>", unsafe_allow_html=True)
                    if todas_analises:
                        df_div = pd.DataFrame(todas_analises, columns=["ID","Texto","Nível","Desc","Área","BaseLegal","Justificativa","Modelo","Fonte","Data","QuestaoID","GabOficial","GabModelo","GabCorreto","QuestionType"])
                        mcq_df = df_div[df_div["QuestaoID"].notnull()]
                        if not mcq_df.empty:
                            acc_por_modelo = mcq_df.groupby("Modelo")["GabCorreto"].mean().reset_index()
                            acc_por_modelo["Acc"] = (acc_por_modelo["GabCorreto"] * 100).round(1)
                            acc_por_modelo["ModeloLabel"] = acc_por_modelo["Modelo"].apply(lambda x: MODELOS.get(x, {}).get("label", x))
                            fig_comp = px.bar(acc_por_modelo, x="ModeloLabel", y="Acc", color="ModeloLabel", text=acc_por_modelo["Acc"].apply(lambda p: f"{p}%"))
                            fig_comp.update_traces(textposition="outside")
                            fig_comp.update_layout(showlegend=False, xaxis_title="", yaxis_title="Acurácia (%)", height=300)
                            st.plotly_chart(fig_comp, use_container_width=True, key="fig_comp_acc")
                        else:
                            st.info("Não há questões de múltipla escolha suficientes para comparar a acurácia.")

                # ── Linha 4: Métricas de qualidade ──────────────────────────────────
                st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background:#f8f9fa;border-radius:10px;padding:20px 24px;margin-bottom:8px'>
                    <p style='font-weight:600;font-size:1rem;margin:0 0 4px'>📐 Métricas de Qualidade da IA</p>
                    <p style='font-size:0.8rem;color:#6c757d;margin:0'>
                    <b>METEOR</b> avalia a correspondência semântica e sinônimos das justificativas.<br>
                    <b>LLM-as-a-Judge</b> usa a Inteligência Artificial para julgar consistência factual baseado em uma amostra de até 5 casos.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                if not pares:
                    st.info("Nenhuma justificativa disponível para cálculo de NLP.")
                else:
                    import nltk
                    from nltk.translate import meteor_score
                    from nltk.tokenize import word_tokenize
                    import random

                    meteor_scores = []
                    
                    # LLM Judge sample
                    amostra_pares = random.sample(pares, min(5, len(pares)))
                    llm_scores = []
                    
                    for texto, justificativa, base_legal in pares:
                        # METEOR Score
                        try:
                            ref_tokens = word_tokenize(texto)
                            hyp_tokens = word_tokenize(justificativa)
                            m_score = meteor_score.meteor_score([ref_tokens], hyp_tokens)
                        except Exception:
                            m_score = 0
                        meteor_scores.append(m_score)

                    with st.spinner("Invocando LLM-as-a-Judge para a amostragem..."):
                        for texto, justificativa, base_legal in amostra_pares:
                             score = avaliar_com_llm_judge(texto, justificativa)
                             llm_scores.append(score)

                    m_med  = sum(meteor_scores)  / len(meteor_scores) if meteor_scores else 0
                    llm_med  = sum(llm_scores)  / len(llm_scores) if llm_scores else 0

                    df_met = pd.DataFrame(todas_analises, columns=["ID","Texto","Nível","Desc","Área","BaseLegal","Justificativa","Modelo","Fonte","Data","QuestaoID","GabOficial","GabModelo","GabCorreto","QuestionType"]) if todas_analises else pd.DataFrame()
                    if not df_met.empty:
                        mcq_df = df_met[df_met["QuestaoID"].notnull() & (df_met["QuestaoID"].astype(str).str.strip() != "") & (df_met["QuestaoID"].astype(str).str.lower() != "none")]
                    else:
                        mcq_df = pd.DataFrame()

                    def gauge(valor, label, cor):
                        fig = px.pie(
                            values=[valor, max(0, 1 - valor)], hole=0.72,
                            color_discrete_sequence=[cor, "#f0f0f0"]
                        )
                        fig.update_traces(textinfo="none", hoverinfo="skip")
                        fig.update_layout(
                            showlegend=False,
                            annotations=[dict(text=f"<b>{valor:.0%}</b>", x=0.5, y=0.5,
                                              font_size=22, showarrow=False, font_color=cor)],
                            margin=dict(t=10, b=10, l=10, r=10), height=180,
                            paper_bgcolor="rgba(0,0,0,0)"
                        )
                        return fig

                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.markdown("<p style='text-align:center;font-weight:600;margin-bottom:0'>METEOR</p>", unsafe_allow_html=True)
                        st.plotly_chart(gauge(m_med, "METEOR", "#0066cc"), use_container_width=True, key=f"g1_{idx}")
                    with m2:
                        st.markdown("<p style='text-align:center;font-weight:600;margin-bottom:0'>LLM Judge (Amostra)</p>", unsafe_allow_html=True)
                        st.plotly_chart(gauge(llm_med, "LLM-Judge", "#8A2BE2"), use_container_width=True, key=f"g2_{idx}")
                    with m3:
                        st.markdown("<p style='text-align:center;font-weight:600;margin-bottom:0'>% Respostas Corretas</p>", unsafe_allow_html=True)
                        if n_corretas is not None and len(mcq_df) > 0:
                            pct_corretas = n_corretas / len(mcq_df)
                            st.plotly_chart(gauge(pct_corretas, "Corretas", "#28a745"), use_container_width=True, key=f"g3_{idx}")
                            st.markdown(f"<p style='text-align:center;font-size:0.8rem;color:#6c757d'>{n_corretas} de {len(mcq_df)} questões</p>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='text-align:center;margin-top:20px;color:#999;'>N/A — sem MCQ</div>", unsafe_allow_html=True)
                    with m4:
                        st.markdown("<p style='text-align:center;font-weight:600;margin-bottom:0'>% Respostas Incorretas</p>", unsafe_allow_html=True)
                        if n_incorretas is not None and len(mcq_df) > 0:
                            pct_incorretas = n_incorretas / len(mcq_df)
                            st.plotly_chart(gauge(pct_incorretas, "Incorretas", "#dc3545"), use_container_width=True, key=f"g4_{idx}")
                            st.markdown(f"<p style='text-align:center;font-size:0.8rem;color:#6c757d'>{n_incorretas} de {len(mcq_df)} questões</p>", unsafe_allow_html=True)
                        else:
                            st.markdown("<p style='text-align:center;font-weight:600;margin-bottom:0'>% Respostas Incorretas</p><div style='text-align:center;margin-top:20px;color:#999;'>N/A</div>", unsafe_allow_html=True)

# ── Página: Consultar Análises ───────────────────────────────────────────────
elif pagina == "🔍 Consultar Análises":
    st.header("🔍 Consultar Análises")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        areas_opcoes = [None] + AREAS
        filtro_area = st.selectbox("Filtrar por Área", areas_opcoes,
                                   format_func=lambda x: "Todas as áreas" if x is None else x.replace("_", " ").title())
    with col2:
        modelos_db = listar_modelos_usados()
        filtro_modelo = st.selectbox("Filtrar por Modelo", [None] + modelos_db,
                                     format_func=lambda x: "Todos os modelos" if x is None else MODELOS.get(x, {}).get("label", x))
    with col3:
        busca = st.text_input("🔎 Buscar no texto", placeholder="Digite palavras-chave...")

    analises = listar_analises(None, filtro_area, filtro_modelo)

    if busca:
        analises = [a for a in analises if busca.lower() in a[1].lower()]

    st.caption(f"**{len(analises)}** registro(s) encontrado(s)")

    if not analises:
        st.info("Nenhuma análise encontrada com os filtros aplicados.")
    else:
        for row in analises:
            id_, texto, nivel, desc_nivel, area, base_legal, justificativa, modelo, fonte, criado_em, qid, gobj, gmod, gcor, qtype = row
            area_fmt = (area or "").replace("_", " ").title()
            # Filtro de qid robusto
            qid = qid if (qid and str(qid).strip() and str(qid).lower() != "none") else None

            with st.expander(f"#{id_} · {area_fmt} · {criado_em[:16]}", expanded=False):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown("**📄 Texto:**")
                    st.markdown(f"<div class='card'>{texto[:500]}{'...' if len(texto) > 500 else ''}</div>", unsafe_allow_html=True)
                    if justificativa:
                        st.markdown(f"**💬 Justificativa/Resposta:** {justificativa}")
                    if qid:
                        st.divider()
                        st.markdown(f"**📝 Questão ID:** `{qid}`")
                        st.markdown(f"**🎯 Gabarito Oficial:** `{gobj}` | **🤖 Resposta do Modelo:** `{gmod}`")
                        if gcor:
                            st.success("✅ Gabarito Correto")
                        else:
                            st.error(f"❌ Gabarito Incorreto — A resposta correta é: `{gmod}`")
                with col_b:
                    st.markdown(f"**🏛️ Área:** {area_fmt}")
                    st.markdown(f"**🤖 Modelo:** `{MODELOS.get(modelo, {}).get('label', modelo)}`")
                    st.markdown(f"**📁 Fonte:** `{fonte}`")
                    st.markdown(f"**🕐 Data:** {criado_em[:16]}")

        # Exportar resultados
        st.divider()
        df_export = pd.DataFrame(analises, columns=["ID","Texto","NívelDB","Desc Nível BD","Área","Base Legal","Justificativa","Modelo","Fonte","Criado Em","Questão ID","Gab. Oficial","Gab. Modelo","Gab. Correto","Tipo Questão"])
        df_export = df_export.drop(columns=["NívelDB","Desc Nível BD","Base Legal"])
        csv_data = df_export.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar resultados (CSV)", csv_data, "analises_juridicas.csv", "text/csv", use_container_width=True)
