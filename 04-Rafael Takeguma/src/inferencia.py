import json
import os
import time
import pandas as pd
from google import genai
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv

# ==========================================
# CONFIGURAÇÕES GLOBAIS E PROMPTS
# ==========================================

INSTRUCAO_SISTEMA = """Você é um Analista Especialista em Exames da OAB.

Você está respondendo a uma questão oficial do Exame de Ordem (OAB). Esta resposta será avaliada por uma banca examinadora que busca clareza, correção jurídica e indicação precisa de dispositivos legais.

- Sempre cite os Artigos da Lei como referência."""

def preparar_contexto_usuario(texto_base, lista_perguntas):
    """Formata o conteúdo da questão para o padrão esperado pelo LLM."""
    bloco_perguntas = "\n".join(lista_perguntas) if isinstance(lista_perguntas, list) else str(lista_perguntas)
    return f"ENUNCIADO:\n{texto_base}\n\nPERGUNTAS:\n{bloco_perguntas}"


def orquestrar_inferencia():
    load_dotenv()
    chave_acesso = os.getenv("GOOGLE_API_KEY")
    if not chave_acesso:
        raise ValueError("ERRO CRÍTICO: Variável GOOGLE_API_KEY ausente no ficheiro .env")

    cliente_ia = genai.Client(api_key=chave_acesso)

    modelos_disponiveis = os.getenv(
        "INFERENCIA_MODELS", 
        "gemini-3.1-flash-lite-preview,gemini-3-flash-preview,gemini-3.1-pro-preview"
    )
    lista_modelos = [mod.strip() for mod in modelos_disponiveis.split(",") if mod.strip()]
    
    if not lista_modelos:
        raise ValueError("ERRO: É necessário definir pelo menos um modelo para teste.")

    ficheiro_origem = os.getenv("INFERENCIA_INPUT_FILE", "dataset_rafael.jsonl")
    ficheiro_destino = os.getenv("INFERENCIA_OUTPUT_FILE", "resultados_gemini_rafael.csv")

    print(f"A carregar ficheiro de questões: {ficheiro_origem}...")
    df_questoes = pd.read_json(ficheiro_origem, lines=True)
    print(f"Total de casos a processar: {len(df_questoes)}\n")


    parametros_geracao = GenerateContentConfig(
        system_instruction=INSTRUCAO_SISTEMA,
        temperature=0.2
    )

    matriz_resultados = []

    for indice, registo in df_questoes.iterrows():
        identificador_questao = registo.get('question_id', f'ID_falha_{indice}')
        print(f"[{indice+1}/{len(df_questoes)}] A processar questão: {identificador_questao}")
        
        prompt_usuario = preparar_contexto_usuario(
            texto_base=registo.get('statement', ''),
            lista_perguntas=registo.get('turns', [])
        )
        
        dados_linha = {
            "question_id": identificador_questao,
            "categoria": registo.get('category', 'Categoria_Nula')
        }
        
        for versao_modelo in lista_modelos:
            print(f"    -> A invocar: {versao_modelo}...")
            try:
                resposta_api = cliente_ia.models.generate_content(
                    model=versao_modelo,
                    contents=prompt_usuario,
                    config=parametros_geracao
                )
                
                dados_linha[versao_modelo] = resposta_api.text
                print("       [SUCESSO] Resposta capturada.")
                
            except Exception as falha:
                print(f"       [ERRO] Falha no modelo {versao_modelo}: {falha}")
                dados_linha[versao_modelo] = f"FALHA_API: {falha}"
                
            
        matriz_resultados.append(dados_linha)
        print("-" * 50)

    print("\nA compilar resultados e a gerar relatório final...")
    tabela_inferencia = pd.DataFrame(matriz_resultados)
    tabela_inferencia.to_csv(ficheiro_destino, index=False, sep=';', encoding='utf-8-sig')
    
    print(f"Operação concluída. Ficheiro guardado em: '{ficheiro_destino}'")

if __name__ == "__main__":
    orquestrar_inferencia()