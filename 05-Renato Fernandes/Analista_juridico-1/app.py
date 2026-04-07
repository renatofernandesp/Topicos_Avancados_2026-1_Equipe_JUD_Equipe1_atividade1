import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from database import init_db, inserir_analise, listar_analises, contar_por_nivel, contar_por_area, salvar_dataset, listar_datasets, excluir_dataset, get_dataset_conteudo, listar_analises_com_justificativa, listar_modelos_usados
from report import gerar_pdf
from analyzer import analisar_lote, NIVEIS, AREAS, MODELOS, avaliar_com_llm_judge
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
    .nivel-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .nivel-1 { background: #d4edda; color: #155724; }
    .nivel-2 { background: #cce5ff; color: #004085; }
    .nivel-3 { background: #fff3cd; color: #856404; }
    .nivel-4 { background: #f8d7da; color: #721c24; }
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

NIVEL_CORES = {1: "#28a745", 2: "#007bff", 3: "#ffc107", 4: "#dc3545"}
NIVEL_LABELS = {1: "Nível 1 · Estagiário", 2: "Nível 2 · Analista", 3: "Nível 3 · Juiz de Direito", 4: "Nível 4 · Ministro STF/STJ"}

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
            type=["json", "csv", "txt"],
            help="JSON: lista de objetos ou strings | CSV: qualquer estrutura | TXT: parágrafos separados por linha em branco"
        )

    with col2:
        st.info("**Formatos aceitos:**\n- **JSON**: lista de objetos ou strings\n- **CSV**: qualquer estrutura tabular\n- **TXT**: parágrafos ou linhas")

    if arquivo:
        conteudo = arquivo.read()
        try:
            registros = parse_arquivo(conteudo, arquivo.name)
            st.success(f"✅ **{len(registros)} registros** encontrados em `{arquivo.name}`")

            with st.expander("👁️ Pré-visualização dos registros", expanded=False):
                for i, r in enumerate(registros[:5]):
                    st.markdown(f"<div class='card'><small><b>#{i+1}</b></small><br>{r[:300]}{'...' if len(r) > 300 else ''}</div>", unsafe_allow_html=True)
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

                sucessos = [r for r in resultados if r["nivel"] > 0]
                erros_list = [r for r in resultados if r["nivel"] == 0]

                if erros_list:
                    st.warning(f"⚠️ {len(erros_list)} registro(s) com erro durante a análise.")
                    with st.expander("👁️ Ver detalhes dos erros"):
                        for erro in erros_list:
                            modelo_label = MODELOS.get(erro.get("modelo"), {}).get("label", erro.get("modelo"))
                            error_message = erro.get('base_legal', 'Erro desconhecido.')
                            st.error(f"**Modelo:** {modelo_label}\n\n**Detalhes:** {error_message}", icon="🚨")

                if sucessos:
                    for r in sucessos:
                        inserir_analise(dataset_id, r["texto"], r["nivel"], r["descricao_nivel"], r["area"], r["base_legal"], r["justificativa"], r["modelo"], r["fonte"])
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
                dados_nivel = contar_por_nivel(modelo_ativo)
                dados_area  = contar_por_area(modelo_ativo)
                pares       = listar_analises_com_justificativa(modelo_ativo)
                total      = sum(r[2] for r in dados_nivel) if dados_nivel else 0
                nivel_map  = {r[0]: r[2] for r in dados_nivel}
                areas_unicas = len(dados_area)
                todas_analises = listar_analises(filtro_modelo=modelo_ativo)

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
                        pdf_bytes = gerar_pdf(
                            total=total, nivel_map=nivel_map, dados_area=dados_area,
                            pares=pares, analises=todas_analises, niveis_dict=NIVEIS,
                            titulo_relatorio="Visão Geral" if modelo_ativo is None else MODELOS.get(modelo_ativo, {}).get("label", modelo_ativo),
                            nome_dataset=dataset_str
                        )
                        sufixo = "Geral" if modelo_ativo is None else modelo_ativo
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
                k1, k2, k3, k4 = st.columns(4)
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

                kpi_card(k1, "📋", "Total Analisado",   total,       "#0066cc")
                kpi_card(k2, "📁", "Datasets Importados", n_datasets, "#6f42c1")
                kpi_card(k3, "🏛️", "Áreas Identificadas", areas_unicas,"#fd7e14")
                nivel_dominante = max(nivel_map, key=nivel_map.get) if nivel_map else 1
                kpi_card(k4, "🏆", "Nível Predominante",
                         f"N{nivel_dominante} · {NIVEIS.get(nivel_dominante, '').split()[0]}", "#28a745")

                st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

                # ── Linha 2: Distribuição por nível (barras) + Área (donut) ─────────
                col_esq, col_dir = st.columns([3, 2], gap="large")

                with col_esq:
                    st.markdown("<p style='font-weight:600;font-size:1rem;margin-bottom:4px'>📊 Distribuição por Nível de Parecer</p>", unsafe_allow_html=True)
                    df_nivel = pd.DataFrame(dados_nivel, columns=["Nível", "Descrição", "Total"])
                    df_nivel["Label"] = df_nivel["Nível"].map(lambda n: NIVEL_LABELS.get(n, str(n)))
                    df_nivel["Cor"]   = df_nivel["Nível"].map(NIVEL_CORES)
                    df_nivel["Pct"]   = (df_nivel["Total"] / total * 100).round(1)
                    fig_nivel = px.bar(
                        df_nivel, x="Label", y="Total",
                        color="Label",
                        color_discrete_sequence=list(NIVEL_CORES.values()),
                        text=df_nivel["Pct"].apply(lambda p: f"{p}%"),
                        custom_data=["Pct"]
                    )
                    fig_nivel.update_traces(textposition="outside", marker_line_width=0)
                    fig_nivel.update_layout(
                        showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(title="", tickfont=dict(size=11)),
                        yaxis=dict(title="Qtd", gridcolor="#f0f0f0"),
                        margin=dict(t=20, b=10, l=0, r=0), height=300
                    )
                    st.plotly_chart(fig_nivel, use_container_width=True, key=f"f1_{idx}")

                with col_dir:
                    st.markdown("<p style='font-weight:600;font-size:1rem;margin-bottom:4px'>🏛️ Áreas Jurídicas</p>", unsafe_allow_html=True)
                    df_area = pd.DataFrame(dados_area, columns=["Área", "Total"])
                    df_area["Área"] = df_area["Área"].str.replace("_", " ").str.title()
                    fig_area = px.pie(
                        df_area, values="Total", names="Área",
                        hole=0.55,
                        color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    fig_area.update_traces(
                        textposition="outside", textinfo="label+percent",
                        pull=[0.03] * len(df_area)
                    )
                    fig_area.update_layout(
                        showlegend=False, margin=dict(t=20, b=20, l=0, r=0),
                        paper_bgcolor="rgba(0,0,0,0)", height=300
                    )
                    st.plotly_chart(fig_area, use_container_width=True, key=f"f2_{idx}")

                # ── Linha 3: Heatmap nível x área ───────────────────────────────────
                st.markdown("<p style='font-weight:600;font-size:1rem;margin:8px 0 4px'>🔥 Concentração: Nível × Área</p>", unsafe_allow_html=True)
                if todas_analises:
                    df_heat = pd.DataFrame(todas_analises,
                        columns=["ID","Texto","Nível","Desc","Área","BaseLegal","Justificativa","Modelo","Fonte","Data"])
                    if not df_heat.empty and "Área" in df_heat.columns and "Nível" in df_heat.columns:
                        df_heat["Área"]  = df_heat["Área"].fillna("").astype(str).str.replace("_"," ").str.title()
                        df_heat["NLabel"] = df_heat["Nível"].map(lambda n: f"N{n} {NIVEIS.get(n,'')[:8]}")
                        pivot = df_heat.groupby(["NLabel","Área"]).size().reset_index(name="Qtd")
                        fig_heat = px.density_heatmap(
                            pivot, x="Área", y="NLabel", z="Qtd",
                            color_continuous_scale="Blues", text_auto=True
                        )
                        fig_heat.update_layout(
                            xaxis=dict(title="", tickangle=-30),
                            yaxis=dict(title=""),
                            coloraxis_showscale=False,
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=10, b=60, l=0, r=0), height=260
                        )
                        st.plotly_chart(fig_heat, use_container_width=True, key=f"f3_{idx}")

                # ── Comparativo entre modelos (apenas na Visão Geral) ────────────────
                if modelo_ativo is None and len(modelos_usados) > 1:
                    st.divider()
                    st.markdown("<p style='font-weight:600;font-size:1.2rem;margin:12px 0 4px'>🤖 Comparativo entre Modelos</p>", unsafe_allow_html=True)
                    MODELO_CORES = ["#0066cc", "#fd7e14", "#28a745", "#dc3545"]
                    comp_cols = st.columns(len(modelos_usados))
                    for m_idx, mk in enumerate(modelos_usados):
                        nd = contar_por_nivel(mk)
                        tot_m = sum(r[2] for r in nd)
                        label = MODELOS.get(mk, {}).get("label", mk)
                        cor   = MODELO_CORES[m_idx % len(MODELO_CORES)]
                        with comp_cols[m_idx]:
                            st.markdown(f"<p style='font-weight:600;color:{cor};text-align:center;margin-bottom:6px'>{label}</p>", unsafe_allow_html=True)
                            if nd:
                                df_c = pd.DataFrame(nd, columns=["Nível","Desc","Total"])
                                df_c["Pct"] = (df_c["Total"]/tot_m*100).round(1)
                                df_c["Label"] = df_c["Nível"].map(lambda n: f"N{n}")
                                fig_c = px.bar(df_c, x="Label", y="Total",
                                            text=df_c["Pct"].apply(lambda p: f"{p}%"),
                                            color_discrete_sequence=[cor])
                                fig_c.update_traces(textposition="outside", marker_line_width=0)
                                fig_c.update_layout(
                                    showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    xaxis=dict(title=""), yaxis=dict(title="Qtd", gridcolor="#f0f0f0"),
                                    margin=dict(t=10, b=10, l=0, r=0), height=220
                                )
                                st.plotly_chart(fig_c, use_container_width=True, key=f"fc_{idx}_{m_idx}")
                                st.caption(f"Total: **{tot_m}** registros")
                            else:
                                st.info("Sem dados")

                    st.markdown("<p style='font-weight:600;font-size:0.9rem;margin:8px 0 4px'>🔍 Divergências de Classificação por Nível</p>", unsafe_allow_html=True)
                    if todas_analises:
                        df_div = pd.DataFrame(todas_analises, columns=["ID","Texto","Nível","Desc","Área","BaseLegal","Justificativa","Modelo","Fonte","Data"])
                        if not df_div.empty:
                            pivot_div = df_div.groupby(["Texto","Modelo"])["Nível"].first().unstack()
                            if pivot_div.shape[1] > 1:
                                divergentes = pivot_div[pivot_div.nunique(axis=1) > 1].reset_index()
                                if not divergentes.empty:
                                    divergentes["Texto"] = divergentes["Texto"].str[:80] + "..."
                                    st.dataframe(divergentes, use_container_width=True, height=200)
                                else:
                                    st.success("✅ Todos os modelos concordaram nas classificações de nível.")

                # ── Linha 4: Métricas de qualidade ──────────────────────────────────
                st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background:#f8f9fa;border-radius:10px;padding:20px 24px;margin-bottom:8px'>
                    <p style='font-weight:600;font-size:1rem;margin:0 0 4px'>📐 Métricas de Qualidade da IA</p>
                    <p style='font-size:0.8rem;color:#6c757d;margin:0'>
                    <b>METEOR</b> avalia a correspondência semântica e sinônimos das justificativas.<br>
                    <b>LLM-as-a-Judge</b> usa a Inteligência Artificial para julgar consistência factual baseado em uma amostra de até 5 casos.<br>
                    <b>Cobertura da Base Legal</b> indica o % de normas identificadas que aparecem no texto fonte.
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

                    meteor_scores, cobertura_scores = [], []
                    
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
                        
                        if base_legal:
                            termos = [t.strip().lower() for t in base_legal.split(",") if t.strip()]
                            encontrados = sum(1 for t in termos if t in texto.lower())
                            cobertura_scores.append(encontrados / len(termos) if termos else 0)
                        else:
                            cobertura_scores.append(0)

                    with st.spinner("Invocando LLM-as-a-Judge para a amostragem..."):
                        for texto, justificativa, base_legal in amostra_pares:
                             score = avaliar_com_llm_judge(texto, justificativa)
                             llm_scores.append(score)

                    m_med  = sum(meteor_scores)  / len(meteor_scores) if meteor_scores else 0
                    llm_med  = sum(llm_scores)  / len(llm_scores) if llm_scores else 0
                    cob_med = sum(cobertura_scores) / len(cobertura_scores) if cobertura_scores else 0

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

                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f"<p style='text-align:center;font-weight:600;margin-bottom:0'>METEOR</p>", unsafe_allow_html=True)
                        st.plotly_chart(gauge(m_med, "METEOR", "#0066cc"), use_container_width=True, key=f"g1_{idx}")
                    with m2:
                        st.markdown(f"<p style='text-align:center;font-weight:600;margin-bottom:0'>LLM Judge (Amostra)</p>", unsafe_allow_html=True)
                        st.plotly_chart(gauge(llm_med, "LLM-Judge", "#8A2BE2"), use_container_width=True, key=f"g2_{idx}")
                    with m3:
                        st.markdown(f"<p style='text-align:center;font-weight:600;margin-bottom:0'>Cobertura Base Legal</p>", unsafe_allow_html=True)
                        st.plotly_chart(gauge(cob_med, "Cobertura", "#28a745"), use_container_width=True, key=f"g3_{idx}")

# ── Página: Consultar Análises ───────────────────────────────────────────────
elif pagina == "🔍 Consultar Análises":
    st.header("🔍 Consultar Análises")

    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        filtro_nivel = st.selectbox("Filtrar por Nível", [None, 1, 2, 3, 4],
                                    format_func=lambda x: "Todos os níveis" if x is None else NIVEL_LABELS[x])
    with col2:
        areas_opcoes = [None] + AREAS
        filtro_area = st.selectbox("Filtrar por Área", areas_opcoes,
                                   format_func=lambda x: "Todas as áreas" if x is None else x.replace("_", " ").title())
    with col3:
        modelos_db = listar_modelos_usados()
        filtro_modelo = st.selectbox("Filtrar por Modelo", [None] + modelos_db,
                                     format_func=lambda x: "Todos os modelos" if x is None else MODELOS.get(x, {}).get("label", x))
    with col4:
        busca = st.text_input("🔎 Buscar no texto", placeholder="Digite palavras-chave...")

    analises = listar_analises(filtro_nivel, filtro_area, filtro_modelo)

    if busca:
        analises = [a for a in analises if busca.lower() in a[1].lower()]

    st.caption(f"**{len(analises)}** registro(s) encontrado(s)")

    if not analises:
        st.info("Nenhuma análise encontrada com os filtros aplicados.")
    else:
        for row in analises:
            id_, texto, nivel, desc_nivel, area, base_legal, justificativa, modelo, fonte, criado_em = row
            nivel_class = f"nivel-{nivel}" if nivel in [1, 2, 3, 4] else "nivel-1"
            area_fmt = (area or "").replace("_", " ").title()

            with st.expander(f"#{id_} · {area_fmt} · {NIVEL_LABELS.get(nivel, 'N/A')} · {criado_em[:16]}", expanded=False):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown("**📄 Texto analisado:**")
                    st.markdown(f"<div class='card'>{texto[:500]}{'...' if len(texto) > 500 else ''}</div>", unsafe_allow_html=True)
                    st.markdown(f"**⚖️ Base Legal:** {base_legal or 'Não identificada'}")
                    if justificativa:
                        st.markdown(f"**💬 Justificativa IA:** {justificativa}")
                with col_b:
                    st.markdown(f"<span class='nivel-badge {nivel_class}'>Nível {nivel} · {desc_nivel}</span>", unsafe_allow_html=True)
                    st.markdown(f"**🏛️ Área:** {area_fmt}")
                    st.markdown(f"**🤖 Modelo:** `{MODELOS.get(modelo, {}).get('label', modelo)}`")
                    st.markdown(f"**📁 Fonte:** `{fonte}`")
                    st.markdown(f"**🕐 Data:** {criado_em[:16]}")

        # Exportar resultados
        st.divider()
        df_export = pd.DataFrame(analises, columns=["ID", "Texto", "Nível", "Descrição Nível", "Área", "Base Legal", "Justificativa", "Modelo", "Fonte", "Criado Em"])
        csv_data = df_export.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar resultados (CSV)", csv_data, "analises_juridicas.csv", "text/csv", use_container_width=True)
