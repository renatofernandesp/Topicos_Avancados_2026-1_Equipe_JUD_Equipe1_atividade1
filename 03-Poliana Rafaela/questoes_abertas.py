
import json
import re
import os
from difflib import SequenceMatcher
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------
# 1. CONFIGURAÇÃO DOS ARQUIVOS
# --------------------------------------------

DATASET_PATH = "Dataset_extarido.txt"

MODEL_FILES = {
    "GPT-5.3": "respostas_gpt5.3_abertas.json",
    "Claude Sonnet 4.6": "respostas_claud.iaSonnet4.6_abertas.json",
    "Gemini": "respostas_gemini_abertas.json",
}

# --------------------------------------------
# 2. FUNÇÕES AUXILIARES
# --------------------------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_dataset_categories(dataset_path):
    """
    Lê o arquivo txt do dataset e extrai a categoria de cada questão.
    O arquivo está em formato textual, não em JSON puro.
    """
    with open(dataset_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Captura as categorias na ordem em que aparecem
    categories = re.findall(r'"category"\s*:\s*"([^"]+)"', text)

    mapping = {}
    for i, cat in enumerate(categories, start=1):
        mapping[f"QUESTION_{i}"] = cat

    return mapping

def normalize_level(classification):
    """
    Converte 'Nível 2 (Analista)' -> 'Nível 2'
    """
    classification = classification or ""
    match = re.search(r'Nível\s*(\d)', classification)
    if match:
        return f"Nível {match.group(1)}"
    return classification.strip()

def macro_category_from_dataset(category):
    """
    Normaliza a categoria do dataset em macrotema.
    """
    cat = (category or "").strip().lower()

    if "direito_administrativo" in cat or "administrativo" in cat:
        return "Direito Administrativo"
    if "direito_civil" in cat or re.search(r"\bcivil\b", cat):
        return "Direito Civil"
    if "direito_constitucional" in cat or "constitucional" in cat:
        return "Direito Constitucional"

    return category

def normalize_area_to_macro(area):
    """
    Normaliza a área da IA para comparar com o macrotema do dataset.
    Ajustei algumas áreas derivadas para bater com a categoria macro.
    """
    area = (area or "").strip().lower()

    if "administrativo" in area:
        return "Direito Administrativo"
    if "constitucional" in area:
        return "Direito Constitucional"
    if "civil" in area:
        return "Direito Civil"

    # Regras de aproximação temática
    if "família" in area or "familia" in area:
        return "Direito Civil"
    if "criança" in area or "adolescente" in area or "eca" in area:
        return "Direito Civil"
    if "digital" in area or "lgpd" in area:
        return "Direito Civil"
    if "processual civil" in area or "execução" in area or "execucao" in area:
        return "Direito Civil"

    return area.title() if area else "Indefinido"

def text_similarity(a, b):
    """
    Similaridade textual simples entre duas respostas.
    Retorna percentual de 0 a 100.
    """
    a = a or ""
    b = b or ""
    return SequenceMatcher(None, a, b).ratio() * 100

def legal_reference_completeness(reference):
    """
    Score aproximado de completude da base legal.
    Não mede correção jurídica. Mede densidade aparente da fundamentação.
    """
    reference = reference or ""
    ref_lower = reference.lower()

    # Conta menções a artigos
    articles_tag = len(re.findall(r'\bart[s]?\b|art\.', ref_lower))

    # Conta números jurídicos: 103, 25, §4º, 61, etc.
    numeric_refs = len(re.findall(r'\b\d+[º°]?(?:,\s*§\s*\d+[º°]?)?', reference))

    # Conta referências complementares relevantes
    complementary_refs = len(re.findall(
        r'súmula|stf|stj|resp|adi|adpf|ritcu|cf/?88|crfb|cpc|cc\b|lgpd|eca|lei',
        ref_lower
    ))

    # Pontuação leve para separadores, indicando mais de uma base legal
    separators = reference.count(";") + reference.count(",")

    score = articles_tag + numeric_refs + complementary_refs + (0.25 * separators)
    return round(score, 3)

def divergence_index(levels_dict, dataset_cat, areas_dict, similarities_dict):
    """
    Índice de divergência por questão, de 0 a 100,
    combinando:
    - divergência na classificação de nível
    - divergência de categoria
    - baixa similaridade textual
    """
    unique_levels = len(set(levels_dict.values()))
    category_mismatches = sum(1 for model in areas_dict if areas_dict[model] != dataset_cat)
    mean_similarity = sum(similarities_dict.values()) / len(similarities_dict)

    # Componentes
    level_component = ((unique_levels - 1) / 2) * 100   # 0, 50 ou 100
    category_component = (category_mismatches / 3) * 100
    similarity_component = 100 - mean_similarity

    # Pesos
    divergence = (
        0.35 * level_component +
        0.30 * category_component +
        0.35 * similarity_component
    )

    return round(divergence, 3)

# --------------------------------------------
# 3. CARREGAMENTO DOS DADOS
# --------------------------------------------

dataset_categories = load_dataset_categories(DATASET_PATH)
model_data = {model: load_json(path) for model, path in MODEL_FILES.items()}

# --------------------------------------------
# 4. CONSOLIDAÇÃO POR QUESTÃO
# --------------------------------------------

rows = []

question_keys = [f"QUESTION_{i}" for i in range(1, 11)]

for q in question_keys:
    dataset_cat_raw = dataset_categories[q]
    dataset_cat_macro = macro_category_from_dataset(dataset_cat_raw)

    answers = {}
    levels = {}
    areas = {}
    legal_refs = {}

    for model_name, data in model_data.items():
        item = data[q]

        answers[model_name] = item.get("model_answer", "")
        levels[model_name] = normalize_level(item.get("classification", ""))
        areas[model_name] = normalize_area_to_macro(item.get("area_of_expertise", ""))
        legal_refs[model_name] = item.get("main_legal_reference", "")

    similarities = {
        "GPT-5.3 x Claude": text_similarity(answers["GPT-5.3"], answers["Claude Sonnet 4.6"]),
        "GPT-5.3 x Gemini": text_similarity(answers["GPT-5.3"], answers["Gemini"]),
        "Claude x Gemini": text_similarity(answers["Claude Sonnet 4.6"], answers["Gemini"]),
    }

    divergence = divergence_index(levels, dataset_cat_macro, areas, similarities)

    row = {
        "Questão": q.replace("QUESTION_", "Q"),
        "Categoria dataset (bruta)": dataset_cat_raw,
        "Categoria dataset (macro)": dataset_cat_macro,

        "Classificação GPT-5.3": levels["GPT-5.3"],
        "Classificação Claude": levels["Claude Sonnet 4.6"],
        "Classificação Gemini": levels["Gemini"],

        "Área GPT-5.3": areas["GPT-5.3"],
        "Área Claude": areas["Claude Sonnet 4.6"],
        "Área Gemini": areas["Gemini"],

        "Similaridade GPT-5.3 x Claude": round(similarities["GPT-5.3 x Claude"], 3),
        "Similaridade GPT-5.3 x Gemini": round(similarities["GPT-5.3 x Gemini"], 3),
        "Similaridade Claude x Gemini": round(similarities["Claude x Gemini"], 3),
        "Similaridade média": round(sum(similarities.values()) / len(similarities), 3),

        "Divergência": divergence,

        "Score base legal GPT-5.3": legal_reference_completeness(legal_refs["GPT-5.3"]),
        "Score base legal Claude": legal_reference_completeness(legal_refs["Claude Sonnet 4.6"]),
        "Score base legal Gemini": legal_reference_completeness(legal_refs["Gemini"]),
    }

    rows.append(row)

df = pd.DataFrame(rows)
print("Tabela consolidada por questão:")
display(df)

# --------------------------------------------
# 5. GRÁFICO 1 - DISTRIBUIÇÃO DOS NÍVEIS POR MODELO
# --------------------------------------------

level_cols = {
    "GPT-5.3": "Classificação GPT-5.3",
    "Claude Sonnet 4.6": "Classificação Claude",
    "Gemini": "Classificação Gemini",
}

level_records = []

for model_name, col in level_cols.items():
    counts = df[col].value_counts()
    for level in ["Nível 1", "Nível 2", "Nível 3", "Nível 4"]:
        level_records.append({
            "Modelo": model_name,
            "Nível": level,
            "Quantidade": int(counts.get(level, 0))
        })

level_df = pd.DataFrame(level_records)

plt.figure(figsize=(9, 5))
for model_name in level_cols.keys():
    sub = level_df[level_df["Modelo"] == model_name]
    plt.plot(sub["Nível"], sub["Quantidade"], marker="o", label=model_name)

plt.title("Gráfico 1: Distribuição dos níveis por modelo")
plt.xlabel("Nível")
plt.ylabel("Quantidade de questões")
plt.legend()
plt.tight_layout()
plt.show()

# --------------------------------------------
# 6. GRÁFICO 2 - ADERÊNCIA À CATEGORIA DO DATASET
# --------------------------------------------

adherence_records = []

area_cols = {
    "GPT-5.3": "Área GPT-5.3",
    "Claude Sonnet 4.6": "Área Claude",
    "Gemini": "Área Gemini",
}

for model_name, area_col in area_cols.items():
    adherent = int((df[area_col] == df["Categoria dataset (macro)"]).sum())
    deviation = int((df[area_col] != df["Categoria dataset (macro)"]).sum())

    adherence_records.append({
        "Modelo": model_name,
        "Tipo": "Aderente",
        "Quantidade": adherent
    })
    adherence_records.append({
        "Modelo": model_name,
        "Tipo": "Desvio",
        "Quantidade": deviation
    })

ad_df = pd.DataFrame(adherence_records)

plt.figure(figsize=(8, 5))
for tipo in ["Aderente", "Desvio"]:
    sub = ad_df[ad_df["Tipo"] == tipo]
    plt.plot(sub["Modelo"], sub["Quantidade"], marker="o", label=tipo)

plt.title("Gráfico 2: Aderência à categoria do dataset")
plt.xlabel("Modelo")
plt.ylabel("Quantidade de questões")
plt.legend()
plt.tight_layout()
plt.show()

print("\nAderência por modelo:")
display(ad_df)

# --------------------------------------------
# 7. GRÁFICO 3 - SIMILARIDADE MÉDIA ENTRE PARES
# --------------------------------------------

pair_means = pd.DataFrame([
    {
        "Par": "GPT-5.3 x Claude",
        "Similaridade média": round(df["Similaridade GPT-5.3 x Claude"].mean(), 3)
    },
    {
        "Par": "GPT-5.3 x Gemini",
        "Similaridade média": round(df["Similaridade GPT-5.3 x Gemini"].mean(), 3)
    },
    {
        "Par": "Claude x Gemini",
        "Similaridade média": round(df["Similaridade Claude x Gemini"].mean(), 3)
    }
])

plt.figure(figsize=(8, 5))
plt.bar(pair_means["Par"], pair_means["Similaridade média"])
plt.title("Gráfico 3: Similaridade média entre pares de modelos")
plt.xlabel("Par de modelos")
plt.ylabel("Similaridade média (%)")
plt.ylim(0, pair_means["Similaridade média"].max() * 1.2)
plt.tight_layout()
plt.show()

print("\nSimilaridade média entre pares:")
display(pair_means)

# --------------------------------------------
# 8. GRÁFICO 4 - DIVERGÊNCIA POR QUESTÃO
# --------------------------------------------

plt.figure(figsize=(9, 5))
plt.bar(df["Questão"], df["Divergência"])
plt.title("Gráfico 4: Índice de divergência por questão")
plt.xlabel("Questão")
plt.ylabel("Índice de divergência (0 a 100)")
plt.ylim(0, df["Divergência"].max() * 1.2)
plt.tight_layout()
plt.show()

print("\nDivergência por questão:")
display(df[["Questão", "Divergência"]].sort_values("Divergência", ascending=False))

# --------------------------------------------
# 9. GRÁFICO 5 - COMPLETUDE DA BASE LEGAL
# --------------------------------------------

legal_scores = pd.DataFrame([
    {
        "Modelo": "GPT-5.3",
        "Score médio": round(df["Score base legal GPT-5.3"].mean(), 3)
    },
    {
        "Modelo": "Claude Sonnet 4.6",
        "Score médio": round(df["Score base legal Claude"].mean(), 3)
    },
    {
        "Modelo": "Gemini",
        "Score médio": round(df["Score base legal Gemini"].mean(), 3)
    }
])

plt.figure(figsize=(8, 5))
plt.bar(legal_scores["Modelo"], legal_scores["Score médio"])
plt.title("Gráfico 5: Completude da base legal por modelo")
plt.xlabel("Modelo")
plt.ylabel("Score médio de completude")
plt.tight_layout()
plt.show()

print("\nScore médio de completude da base legal:")
display(legal_scores)

# --------------------------------------------
# 10. EXPORTAÇÃO OPCIONAL
# --------------------------------------------

# Salvar tabela principal
df.to_csv("metricas_por_questao.csv", index=False, encoding="utf-8-sig")

# Salvar Excel
with pd.ExcelWriter("metricas_graficos_llms.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Por_questao")
    level_df.to_excel(writer, index=False, sheet_name="Grafico_1")
    ad_df.to_excel(writer, index=False, sheet_name="Grafico_2")
    pair_means.to_excel(writer, index=False, sheet_name="Grafico_3")
    legal_scores.to_excel(writer, index=False, sheet_name="Grafico_5")

# Salvar gráficos
plt.figure(figsize=(9, 5))
for model_name in level_cols.keys():
    sub = level_df[level_df["Modelo"] == model_name]
    plt.plot(sub["Nível"], sub["Quantidade"], marker="o", label=model_name)
plt.title("Gráfico 1: Distribuição dos níveis por modelo")
plt.xlabel("Nível")
plt.ylabel("Quantidade de questões")
plt.legend()
plt.tight_layout()
plt.savefig("grafico_1_distribuicao_niveis.png", dpi=200)
plt.close()

plt.figure(figsize=(8, 5))
for tipo in ["Aderente", "Desvio"]:
    sub = ad_df[ad_df["Tipo"] == tipo]
    plt.plot(sub["Modelo"], sub["Quantidade"], marker="o", label=tipo)
plt.title("Gráfico 2: Aderência à categoria do dataset")
plt.xlabel("Modelo")
plt.ylabel("Quantidade de questões")
plt.legend()
plt.tight_layout()
plt.savefig("grafico_2_aderencia_categoria.png", dpi=200)
plt.close()

plt.figure(figsize=(8, 5))
plt.bar(pair_means["Par"], pair_means["Similaridade média"])
plt.title("Gráfico 3: Similaridade média entre pares de modelos")
plt.xlabel("Par de modelos")
plt.ylabel("Similaridade média (%)")
plt.ylim(0, pair_means["Similaridade média"].max() * 1.2)
plt.tight_layout()
plt.savefig("grafico_3_similaridade_pares.png", dpi=200)
plt.close()

plt.figure(figsize=(9, 5))
plt.bar(df["Questão"], df["Divergência"])
plt.title("Gráfico 4: Índice de divergência por questão")
plt.xlabel("Questão")
plt.ylabel("Índice de divergência (0 a 100)")
plt.ylim(0, df["Divergência"].max() * 1.2)
plt.tight_layout()
plt.savefig("grafico_4_divergencia_questao.png", dpi=200)
plt.close()

plt.figure(figsize=(8, 5))
plt.bar(legal_scores["Modelo"], legal_scores["Score médio"])
plt.title("Gráfico 5: Completude da base legal por modelo")
plt.xlabel("Modelo")
plt.ylabel("Score médio de completude")
plt.tight_layout()
plt.savefig("grafico_5_completude_base_legal.png", dpi=200)
plt.close()

print("\nArquivos gerados com sucesso:")
print("- metricas_por_questao.csv")
print("- metricas_graficos_llms.xlsx")
print("- grafico_1_distribuicao_niveis.png")
print("- grafico_2_aderencia_categoria.png")
print("- grafico_3_similaridade_pares.png")
print("- grafico_4_divergencia_questao.png")
print("- grafico_5_completude_base_legal.png")