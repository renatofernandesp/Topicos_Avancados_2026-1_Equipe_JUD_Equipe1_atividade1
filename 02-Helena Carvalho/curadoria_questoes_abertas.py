import json
import pandas as pd
import time
from openai import OpenAI

API_KEY = ""
client = OpenAI(api_key=API_KEY)

caminho_entrada = 'dataset_helena.jsonl'
questoes = []

with open(caminho_entrada, 'r', encoding='utf-8') as f:
    for linha in f:
        if linha.strip():
            questoes.append(json.loads(linha))

print(f"Total de questões para curadoria: {len(questoes)}")

metadados_curadoria = []

for q in questoes:
    q_id = q.get('question_id', 'ID_Desconhecido')
    print(f"Curando questão: {q_id}...")
    
    statement = q.get('statement', '')
    turns = "\n".join(q.get('turns', []))

    prompt_curadoria = f"""
### 1. PERSONA
Você é um Professor Especialista em Direito e Consultor de Curadoria de Dados Jurídicos, com profundo conhecimento do Exame de Ordem da OAB e da prática processual nos tribunais.

### 2. CONTEXTUALIZAÇÃO
Estamos realizando a curadoria de um dataset de questões ABERTAS (Discursivas e Peças Profissionais) da OAB. Sua tarefa é classificar tecnicamente o enunciado para entender o nível de complexidade jurídica e a área envolvida.

### 3. DEFINIÇÕES E CRITÉRIOS
Níveis de Dificuldade:
- Nível 1 Estagiário: Questões discursivas de resposta direta na lei (literalidade).
- Nível 2 Analista: Exige conhecimento de ritos, prazos ou competência básica.
- Nível 3 Juiz de Direito: Casos práticos complexos que exigem subsunção do fato à norma e redação de teses jurídicas.
- Nível 4 Ministro (STF/STJ): Questões envolvendo controle de constitucionalidade, súmulas vinculantes ou peças processuais de alta complexidade.

Áreas de Especialidade Permitidas:
[direito_administrativo, direito_civil, direito_constitucional, direito_do_trabalho, direito_empresarial, direito_penal, direito_tributario]

### 4. INSTRUÇÕES EXPLÍCITAS
1. Analise o ENUNCIADO (caso fático) e as PERGUNTAS/COMANDOS fornecidos.
2. Identifique a área de especialidade dentro da lista permitida.
3. Determine o nível de dificuldade considerando a complexidade da peça ou das respostas exigidas.
4. Indique a referência legal principal (Artigo, Lei ou Súmula) necessária para fundamentar a solução do caso.
5. Diferencie se é uma "Questão Discursiva" ou "Peça Profissional" no campo de observação.

DADOS DA QUESTÃO:
ENUNCIADO: {statement}
PERGUNTAS/COMANDOS: {turns}

### 5. FORMATO DE SAÍDA ESTRUTURADO
Responda obrigatoriamente no formato JSON puro, sem markdown:
{{
    "area": "nome_da_area",
    "dificuldade": "Nível X - Nome",
    "referencia_principal": "Art. X da Lei Y",
    "tipo_questao": "Peça Profissional ou Discursiva"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano-2026-03-17",
            messages=[{"role": "user", "content": prompt_curadoria}],
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        curadoria_json = json.loads(response.choices[0].message.content)
        
        curadoria_json['question_id'] = q_id
        metadados_curadoria.append(curadoria_json)
        print(f"  [OK] Classificada como: {curadoria_json['dificuldade']}")

    except Exception as e:
        print(f"  [ERRO] na questão {q_id}: {e}")
        metadados_curadoria.append({
            "question_id": q_id,
            "area": "ERRO",
            "dificuldade": "ERRO",
            "referencia_principal": str(e),
            "tipo_questao": "ERRO"
        })

    time.sleep(1)

df_curadoria = pd.DataFrame(metadados_curadoria)
df_curadoria.to_csv('curadoria_equipe1_helena.csv', index=False, sep=';', encoding='utf-8-sig')

print("\nCuradoria concluída com sucesso! Arquivo 'curadoria_equipe1_helena.csv' gerado.")