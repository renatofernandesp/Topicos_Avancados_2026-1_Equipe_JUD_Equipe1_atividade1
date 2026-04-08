import json
import pandas as pd
import time
from openai import OpenAI

API_KEY = ""
client = OpenAI(api_key=API_KEY)

modelos_para_testar = [
    'gpt-5.4-nano-2026-03-17',
    'gpt-5-nano-2025-08-07',
    'gpt-4.1-nano-2025-04-14'
]

caminho_arquivo = 'dataset_helena.jsonl'
questoes = []

with open(caminho_arquivo, 'r', encoding='utf-8') as f:
    for linha in f:
        if linha.strip():
            questoes.append(json.loads(linha))

print(f"Total de questões carregadas: {len(questoes)}")

resultados_finais = []

for q in questoes:
    q_id = q.get('question_id', 'ID_Desconhecido')
    print(f"\nProcessando questão: {q_id}...")
    
    system_prompt = q.get('system', 'Você é um assistente jurídico experiente.')
    statement = q.get('statement', '')
    turns = "\n".join(q.get('turns', []))
    
    conteudo_usuario = f"""
### 1. PERSONA
Você é um Advogado Especialista em Exames da OAB, reconhecido pela precisão técnica e rigor na fundamentação legal.

### 2. CONTEXTUALIZAÇÃO
Você está respondendo a uma questão oficial do Exame de Ordem (OAB). Esta resposta será avaliada por uma banca examinadora que busca clareza, correção jurídica e indicação precisa de dispositivos legais.

### 3. DEFINIÇÕES E CRITÉRIOS
- Se for uma PEÇA PRÁTICA: Utilize a estrutura formal (Endereçamento, Fatos, Fundamentação Jurídica e Pedidos).
- Se for uma QUESTÃO DISCURSIVA: Seja direto, responda aos itens (A, B) separadamente e fundamente cada resposta.
- NÃO se identifique: Use "Advogado..." ou "OAB/XXX". Jamais invente dados que não estão no enunciado.

### 4. INSTRUÇÕES EXPLÍCITAS
- Cite sempre os Artigos da Lei (Código Civil, Penal, CPC, CPP, etc.) ou Súmulas aplicáveis.
- Utilize a norma culta do português jurídico.
- Resolva o problema jurídico apresentado de forma exaustiva.

### 5. DADOS DA QUESTÃO
ENUNCIADO:
{statement}

PERGUNTAS/COMANDOS:
{turns}
"""
    
    linha_resultado = {
        "question_id": q_id,
        "categoria": q.get('category', '')
    }
    
    for nome_modelo in modelos_para_testar:
        print(f"  -> Consultando {nome_modelo}...")
        try:
            parametros_api = {
                "model": nome_modelo,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": conteudo_usuario}
                ]
            }
            
            if nome_modelo == 'gpt-5-nano-2025-08-07':
                parametros_api["temperature"] = 1 
            else:
                parametros_api["temperature"] = 0.2 
                
            response = client.chat.completions.create(**parametros_api)
            
            resposta_texto = response.choices[0].message.content
            linha_resultado[nome_modelo] = resposta_texto
            print("  [OK] Resposta gerada.")
            
        except Exception as e:
            print(f"  [ERRO] {nome_modelo}: {e}")
            linha_resultado[nome_modelo] = f"ERRO: {e}"
            
        time.sleep(5) 
        
    resultados_finais.append(linha_resultado)

df_resultados = pd.DataFrame(resultados_finais)
nome_arquivo_saida = "resultados_openai_equipe1_helena.csv"
df_resultados.to_csv(nome_arquivo_saida, index=False, sep=';', encoding='utf-8-sig')

print(f"\nConcluído! Resultados salvos em: {nome_arquivo_saida}")