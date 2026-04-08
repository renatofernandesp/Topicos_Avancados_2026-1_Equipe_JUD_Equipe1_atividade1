import json
import pandas as pd
import time
from openai import OpenAI
from datasets import load_dataset

API_KEY = ""
client = OpenAI(api_key=API_KEY)

ds = load_dataset("eduagarcia/oab_exams")
train_ds = ds['train']

lote_helena = train_ds.select(range(424, 530))

dados_curadoria = []

print(f"Iniciando curadoria ({len(lote_helena)} questões)...")

for i, item in enumerate(lote_helena):
    num_questao = 425 + i
    
    choices = item['choices']
    alternativas = "\n".join([f"{l}) {t}" for l, t in zip(choices['label'], choices['text'])])
    
    prompt = f"""
    ### 1. PERSONA
    Você é um Professor Especialista em Direito e Consultor de Curadoria de Dados Jurídicos, com profundo conhecimento do Exame de Ordem da OAB e da jurisprudência dos tribunais superiores.

    ### 2. CONTEXTUALIZAÇÃO
    Estamos realizando uma atividade de curadoria de um dataset de questões da OAB para treinar modelos de linguagem. Sua tarefa é classificar tecnicamente cada questão para que possamos entender o nível de exigência cognitiva e a área do Direito envolvida.

    ### 3. DEFINIÇÕES E CRITÉRIOS
    Níveis de Dificuldade:
    - Nível 1 Estagiário: Questões de aplicação direta da lei (literalidade).
    - Nível 2 Analista: Questões que exigem conhecimento de ritos processuais ou prazos.
    - Nível 3 Juiz de Direito: Questões que exigem interpretação de casos práticos e subsunção do fato à norma.
    - Nível 4 Ministro (STF/STJ): Questões complexas envolvendo controle de constitucionalidade, súmulas vinculantes ou jurisprudência consolidada.

    Áreas de Especialidade Permitidas:
    [direito_administrativo, direito_civil, direito_constitucional, direito_do_trabalho, direito_empresarial, direito_penal, direito_tributario]

    ### 4. INSTRUÇÕES EXPLÍCITAS
    1. Analise o enunciado e as alternativas fornecidas.
    2. Identifique a área de especialidade dentro da lista permitida.
    3. Determine o nível de dificuldade com base nos critérios acima.
    4. Indique a referência legal exata (Artigo, Lei, Súmula) que fundamenta o gabarito.
    5. Seja técnico e preciso. Se o gabarito for {item['answerKey']}, foque na explicação desta alternativa.

    DADOS DA QUESTÃO:
    ENUNCIADO: {item['question']}
    ALTERNATIVAS: {alternativas}
    GABARITO: {item['answerKey']}

    ### 5. FORMATO DE SAÍDA ESTRUTURADO
    Responda obrigatoriamente no formato JSON:
    {{
        "area": "nome_da_area",
        "dificuldade": "Nível X - Nome",
        "referencia": "Art. X da Lei Y"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        resultado = json.loads(response.choices[0].message.content)
        
        dados_curadoria.append({
            "question_number": num_questao,
            "id_original": item['id'],
            "area": resultado.get('area'),
            "dificuldade": resultado.get('dificuldade'),
            "referencia": resultado.get('referencia'),
            "gabarito": item['answerKey']
        })
        print(f"[{num_questao}] Classificada: {resultado.get('area')} | {resultado.get('dificuldade')}")

    except Exception as e:
        print(f"Erro na questão {num_questao}: {e}")
        time.sleep(5)

    time.sleep(1) 

df = pd.DataFrame(dados_curadoria)
df.to_csv("curadoria_consolidada_helena.csv", index=False, sep=';', encoding='utf-8-sig')
print("\nProcesso concluído! Arquivo 'curadoria_consolidada_helena.csv' gerado.")