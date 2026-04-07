import json
import csv
import io
import pandas as pd

def parse_arquivo(conteudo_bytes: bytes, nome_arquivo: str) -> list[str]:
    ext = nome_arquivo.lower().split(".")[-1]

    if ext == "json":
        return _parse_json(conteudo_bytes)
    elif ext == "csv":
        return _parse_csv(conteudo_bytes)
    else:
        conteudo = conteudo_bytes.decode("utf-8", errors="replace")
        return _parse_txt(conteudo)

def _parse_json(conteudo_bytes: bytes) -> list[str]:
    conteudo = conteudo_bytes.decode("utf-8", errors="replace")
    try:
        data = json.loads(conteudo)
    except Exception:
        return []

    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        return []

    return _process_dataframe(df)

def _parse_csv(conteudo_bytes: bytes) -> list[str]:
    # Tenta diferentes encodings
    for encoding in ['utf-8', 'latin1', 'cp1252']:
        try:
            conteudo = conteudo_bytes.decode(encoding)
            # Lê o CSV e detecta automaticamente o separador (, ou ;)
            df = pd.read_csv(io.StringIO(conteudo), sep=None, engine='python')
            return _process_dataframe(df)
        except Exception:
            continue
    return []

def _process_dataframe(df: pd.DataFrame) -> list[str]:
    textos = []
    
    # Procura coluna de ID para ordenar cronologicamente como desejado
    id_col = next((col for col in df.columns if str(col).strip().lower() == 'id'), None)
    
    if id_col:
        # Ordena usando valor numérico se possível
        df['_temp_sort_id'] = pd.to_numeric(df[id_col], errors='coerce')
        df = df.sort_values('_temp_sort_id').drop(columns=['_temp_sort_id'])
        
    for _, row in df.iterrows():
        parts = []
        for col, val in row.items():
            if pd.notna(val) and str(val).strip():
                parts.append(f"{col}: {val}")
        
        texto = " | ".join(parts)
        if texto.strip():
            textos.append(texto)
            
    return textos

def _parse_txt(conteudo: str) -> list[str]:
    # Divide por linhas em branco (parágrafos) ou por linha
    blocos = [b.strip() for b in conteudo.split("\n\n") if b.strip()]
    if len(blocos) <= 1:
        blocos = [l.strip() for l in conteudo.splitlines() if l.strip()]
    return blocos
