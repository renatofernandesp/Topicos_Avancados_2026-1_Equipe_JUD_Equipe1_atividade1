
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------
# 1. DADOS CONSOLIDADOS
# ------------------------------------------

total_questoes = 106

dados = [
    {
        "Modelo": "Claude Sonnet 4.6",
        "Acertos": 83,
    },
    {
        "Modelo": "ChatGPT 5.3",
        "Acertos": 69,
    },
    {
        "Modelo": "Gemini",
        "Acertos": 45,
    },
]

df = pd.DataFrame(dados)

# ------------------------------------------
# 2. MÉTRICAS
# ------------------------------------------

df["Erros"] = total_questoes - df["Acertos"]
df["Acurácia"] = df["Acertos"] / total_questoes
df["Taxa de Erro"] = df["Erros"] / total_questoes

# Em questões fechadas, Exact Match = Acurácia
df["Exact Match (EM)"] = df["Acurácia"]

# Formato percentual
df["Acurácia (%)"] = (df["Acurácia"] * 100).round(2)
df["Taxa de Erro (%)"] = (df["Taxa de Erro"] * 100).round(2)
df["Exact Match (EM) (%)"] = (df["Exact Match (EM)"] * 100).round(2)

print("Tabela consolidada:")
display(df)

# ------------------------------------------
# 3. GRÁFICO 1 - ACURÁCIA
# ------------------------------------------

plt.figure(figsize=(8, 5))
plt.bar(df["Modelo"], df["Acurácia (%)"])
plt.title("Gráfico 1: Acurácia por modelo")
plt.xlabel("Modelo")
plt.ylabel("Acurácia (%)")
plt.ylim(0, 100)

for i, v in enumerate(df["Acurácia (%)"]):
    plt.text(i, v + 1, f"{v:.2f}%", ha="center")

plt.tight_layout()
plt.show()

# ------------------------------------------
# 4. GRÁFICO 2 - TAXA DE ERRO
# ------------------------------------------

plt.figure(figsize=(8, 5))
plt.bar(df["Modelo"], df["Taxa de Erro (%)"])
plt.title("Gráfico 2: Taxa de erro por modelo")
plt.xlabel("Modelo")
plt.ylabel("Taxa de erro (%)")
plt.ylim(0, 100)

for i, v in enumerate(df["Taxa de Erro (%)"]):
    plt.text(i, v + 1, f"{v:.2f}%", ha="center")

plt.tight_layout()
plt.show()

# ------------------------------------------
# 5. GRÁFICO 3 - EXACT MATCH
# ------------------------------------------

plt.figure(figsize=(8, 5))
plt.bar(df["Modelo"], df["Exact Match (EM) (%)"])
plt.title("Gráfico 3: Exact Match (EM) por modelo")
plt.xlabel("Modelo")
plt.ylabel("Exact Match (%)")
plt.ylim(0, 100)

for i, v in enumerate(df["Exact Match (EM) (%)"]):
    plt.text(i, v + 1, f"{v:.2f}%", ha="center")

plt.tight_layout()
plt.show()

# ------------------------------------------
# 6. GRÁFICO 4 - ACERTOS X ERROS
# ------------------------------------------

x = range(len(df))
width = 0.35

plt.figure(figsize=(9, 5))
plt.bar([i - width/2 for i in x], df["Acertos"], width=width, label="Acertos")
plt.bar([i + width/2 for i in x], df["Erros"], width=width, label="Erros")

plt.xticks(list(x), df["Modelo"])
plt.title("Gráfico 4: Acertos x Erros por modelo")
plt.xlabel("Modelo")
plt.ylabel("Quantidade")
plt.legend()

for i, v in enumerate(df["Acertos"]):
    plt.text(i - width/2, v + 1, str(v), ha="center")
for i, v in enumerate(df["Erros"]):
    plt.text(i + width/2, v + 1, str(v), ha="center")

plt.tight_layout()
plt.show()

# ------------------------------------------
# 7. GRÁFICO 5 - VISÃO COMPARATIVA DAS MÉTRICAS
# ------------------------------------------

metricas = ["Acurácia (%)", "Taxa de Erro (%)", "Exact Match (EM) (%)"]

plt.figure(figsize=(10, 6))

for modelo in df["Modelo"]:
    sub = df[df["Modelo"] == modelo]
    valores = [sub[m].values[0] for m in metricas]
    plt.plot(metricas, valores, marker="o", label=modelo)

plt.title("Gráfico 5: Comparação geral das métricas")
plt.xlabel("Métrica")
plt.ylabel("Percentual")
plt.ylim(0, 100)
plt.legend()
plt.tight_layout()
plt.show()

# ------------------------------------------
# 8. EXPORTAÇÃO OPCIONAL
# ------------------------------------------

df.to_csv("resultado_questoes_fechadas_metricas.csv", index=False, encoding="utf-8-sig")

with pd.ExcelWriter("resultado_questoes_fechadas_metricas.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Metricas")

print("Arquivos gerados:")
print("- resultado_questoes_fechadas_metricas.csv")
print("- resultado_questoes_fechadas_metricas.xlsx")