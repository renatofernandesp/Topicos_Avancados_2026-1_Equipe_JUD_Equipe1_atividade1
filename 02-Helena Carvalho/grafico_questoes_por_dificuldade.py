import pandas as pd
import csv
import matplotlib.pyplot as plt

df = pd.read_csv(
    'curadoria_consolidada_helena.csv',
    sep=';',
    engine='python',
    on_bad_lines='skip',
    quotechar='"',
    quoting=csv.QUOTE_MINIMAL
)

def limpar_dificuldade(texto):
    if pd.isna(texto):
        return "Indefinido"
    if 'Nível 1' in texto: return 'Nível 1 - Estagiário'
    if 'Nível 2' in texto: return 'Nível 2 - Analista'
    if 'Nível 3' in texto: return 'Nível 3 - Juiz de Direito'
    if 'Nível 4' in texto: return 'Nível 4 - Ministro (STF/STJ)'
    return texto

df['dificuldade_limpa'] = df['dificuldade'].apply(limpar_dificuldade)

ordem = [
    'Nível 1 - Estagiário',
    'Nível 2 - Analista',
    'Nível 3 - Juiz de Direito',
    'Nível 4 - Ministro (STF/STJ)'
]
contagem = df['dificuldade_limpa'].value_counts().reindex(ordem).fillna(0)

plt.style.use('seaborn-v0_8-muted') 
fig, ax = plt.subplots(figsize=(10, 6))

pastel_greens = ['#d8f3dc', '#b7e4c7', '#95d5b2', '#74c69d']

bars = ax.bar(contagem.index, contagem.values, color=pastel_greens, edgecolor='#40916c', linewidth=1.2)

for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{int(height)}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=11, fontweight='bold', color='#2d6a4f')

ax.set_title('Distribuição de Questões por Nível de Dificuldade', fontsize=16, fontweight='bold', pad=20, color='#1b4332')
ax.set_ylabel('Quantidade de Questões', fontsize=12, labelpad=10, color='#2d6a4f')
ax.set_xlabel('Nível de Competência', fontsize=12, labelpad=10, color='#2d6a4f')

ax.yaxis.grid(True, linestyle='--', alpha=0.4, color='#95d5b2')
ax.set_axisbelow(True)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
ax.spines['left'].set_color('#74c69d')
ax.spines['bottom'].set_color('#74c69d')

plt.xticks(rotation=0, fontsize=10)
plt.tight_layout()

plt.savefig('grafico_dificuldade_profissional.png', dpi=300, bbox_inches='tight')

print("Gráfico gerado com sucesso.")