import os
import json
import httpx
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv

load_dotenv()

NIVEIS = {
    1: "Estagiário",
    2: "Analista",
    3: "Juiz de Direito",
    4: "Ministro (STF/STJ)"
}

AREAS = [
    "direito_administrativo",
    "direito_civil",
    "direito_constitucional",
    "direito_do_trabalho",
    "direito_empresarial",
    "direito_penal",
    "direito_tributario"
]

# ── Configurações dos modelos disponíveis ────────────────────────────────────
MODELOS = {
    "gpt-4o-mini": {
        "label": "GPT-4o Mini",
        "client": AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        ),
        "deployment": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini"),
    },
    "gpt-5.4-nano": {
        "label": "GPT-5.4 Nano",
        "client": AzureOpenAI(
            api_key=os.getenv("NANO_API_KEY"),
            azure_endpoint=os.getenv("NANO_ENDPOINT"),
            api_version=os.getenv("NANO_API_VERSION"),
        ),
        "deployment": os.getenv("NANO_DEPLOYMENT", "gpt-5.4-nano"),
    },
    "llama-4-maverick": {
        "label": "Llama 4 Maverick 17B",
        "client": OpenAI(
            api_key=os.getenv("LLAMA_API_KEY", ""),
            base_url=os.getenv("LLAMA_ENDPOINT", ""),
            default_query={"api-version": "2024-05-01-preview"},
            http_client=httpx.Client(verify=False)
        ),
        "deployment": os.getenv("LLAMA_DEPLOYMENT", "Llama-4-Maverick-17B-128E-Instruct-FP8"),
    }
}

SYSTEM_PROMPT = """Você é um especialista jurídico brasileiro. Analise o texto jurídico fornecido e retorne um JSON com:
- "nivel": número de 1 a 4 indicando quem deve dar o parecer:
  1 = Estagiário (aplicação direta da lei, literalidade)
  2 = Analista (ritos processuais ou prazos)
  3 = Juiz de Direito (interpretação de casos práticos, subsunção do fato à norma)
  4 = Ministro STF/STJ (controle de constitucionalidade, súmulas vinculantes, conflitos de leis)
- "area": uma das áreas: direito_administrativo, direito_civil, direito_constitucional, direito_do_trabalho, direito_empresarial, direito_penal, direito_tributario
- "base_legal": lista das principais normas, artigos, leis ou súmulas aplicáveis (máximo 5 itens)
- "justificativa": breve justificativa da classificação (máximo 2 frases)

Responda APENAS com o JSON, sem markdown."""

def analisar_texto(texto: str, modelo_key: str) -> dict:
    modelo = MODELOS[modelo_key]
    
    kwargs = {
        "model": modelo["deployment"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Texto jurídico:\n{texto[:3000]}"}
        ],
        "temperature": 0.1
    }
    
    # Modelos novos (o1, gpt-4o, etc) usam max_completion_tokens. Modelos antigos max_tokens
    if modelo_key in ["gpt-5.4-nano"]:
        kwargs["max_completion_tokens"] = 500
    else:
        kwargs["max_tokens"] = 500

    response = modelo["client"].chat.completions.create(**kwargs)
    
    content = response.choices[0].message.content.strip()
    # remove markdown code block se o modelo retornar
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    result = json.loads(content)
    nivel = int(result.get("nivel", 1))
    return {
        "nivel": nivel,
        "descricao_nivel": NIVEIS.get(nivel, "Desconhecido"),
        "area": result.get("area", "direito_civil"),
        "base_legal": ", ".join(result.get("base_legal", [])) if isinstance(result.get("base_legal"), list) else result.get("base_legal", ""),
        "justificativa": result.get("justificativa", ""),
        "modelo": modelo_key,
    }

def avaliar_com_llm_judge(texto: str, justificativa: str, modelo_judge="gpt-4o-mini") -> float:
    if modelo_judge not in MODELOS:
        modelo_judge = list(MODELOS.keys())[0]
        
    modelo = MODELOS[modelo_judge]
    prompt = f"""TEXTO ORIGINAL:
{texto}
JUSTIFICATIVA GERADA:
{justificativa}
Atribua uma nota rígida de 0.0 a 1.0 representando o quão semanticamente precisa, consistente e factualmente correta a justificativa é considerando apenas os fatos presentes no texto original.
Retorne APENAS o número decimal (ex: 0.85). Não escreva texto."""

    kwargs = {
        "model": modelo["deployment"],
        "messages": [
            {"role": "system", "content": "Você é um robô juiz que só responde com notas float."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
    }
    if modelo_judge in ["gpt-5.4-nano"]:
        kwargs["max_completion_tokens"] = 10
    else:
        kwargs["max_tokens"] = 10

    try:
        response = modelo["client"].chat.completions.create(**kwargs)
        content = response.choices[0].message.content.strip()
        import re
        match = re.search(r"(?:0\.\d+|1\.0|\d+)", content)
        if match:
            nota = float(match.group())
            return min(max(nota, 0.0), 1.0)
    except Exception:
        pass
    return 0.0


def analisar_lote(registros: list[str], fonte: str, modelos_selecionados: list[str], progress_callback=None) -> list[dict]:
    resultados = []
    total_ops = len(registros) * len(modelos_selecionados)
    contador = 0
    for texto in registros:
        if not texto or not texto.strip():
            continue
        for modelo_key in modelos_selecionados:
            try:
                analise = analisar_texto(texto, modelo_key)
                analise["texto"] = texto
                analise["fonte"] = fonte
                resultados.append(analise)
            except Exception as e:
                resultados.append({
                    "texto": texto,
                    "nivel": 0,
                    "descricao_nivel": "Erro",
                    "area": "indefinido",
                    "base_legal": f"Erro: {str(e)}",
                    "justificativa": "",
                    "modelo": modelo_key,
                    "fonte": fonte
                })
            contador += 1
            if progress_callback:
                progress_callback(contador, total_ops)
    return resultados
