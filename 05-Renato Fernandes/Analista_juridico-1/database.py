import sqlite3

DB_PATH = "juridico.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                conteudo BLOB NOT NULL,
                total_registros INTEGER,
                importado_em TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
                texto TEXT NOT NULL,
                nivel_parecer INTEGER,
                descricao_nivel TEXT,
                area_especialidade TEXT,
                base_legal TEXT,
                justificativa TEXT,
                modelo TEXT DEFAULT 'gpt-4o-mini',
                fonte_arquivo TEXT,
                criado_em TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()

def salvar_dataset(nome, conteudo_bytes, total_registros):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO datasets (nome, conteudo, total_registros) VALUES (?, ?, ?)
        """, (nome, conteudo_bytes, total_registros))
        conn.commit()
        return cursor.lastrowid

def listar_datasets():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, nome, total_registros, importado_em FROM datasets ORDER BY importado_em DESC
        """).fetchall()

def excluir_dataset(dataset_id):
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
        conn.commit()

def get_dataset_conteudo(dataset_id):
    with get_connection() as conn:
        row = conn.execute("SELECT nome, conteudo FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
    return row

def inserir_analise(dataset_id, texto, nivel, descricao_nivel, area, base_legal, justificativa, modelo, fonte):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO analises (dataset_id, texto, nivel_parecer, descricao_nivel, area_especialidade, base_legal, justificativa, modelo, fonte_arquivo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (dataset_id, texto, nivel, descricao_nivel, area, base_legal, justificativa, modelo, fonte))
        conn.commit()

def listar_analises(filtro_nivel=None, filtro_area=None, filtro_modelo=None):
    query = "SELECT id, texto, nivel_parecer, descricao_nivel, area_especialidade, base_legal, justificativa, modelo, fonte_arquivo, criado_em FROM analises WHERE 1=1"
    params = []
    if filtro_nivel:
        query += " AND nivel_parecer = ?"
        params.append(filtro_nivel)
    if filtro_area:
        query += " AND area_especialidade = ?"
        params.append(filtro_area)
    if filtro_modelo:
        query += " AND modelo = ?"
        params.append(filtro_modelo)
    query += " ORDER BY criado_em DESC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return rows

def listar_analises_com_justificativa(filtro_modelo=None):
    query = """
        SELECT texto, justificativa, base_legal FROM analises
        WHERE justificativa IS NOT NULL AND justificativa != ''
    """
    params = []
    if filtro_modelo:
        query += " AND modelo = ?"
        params.append(filtro_modelo)
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()

def contar_por_nivel(filtro_modelo=None):
    query = "SELECT nivel_parecer, descricao_nivel, COUNT(*) as total FROM analises"
    params = []
    if filtro_modelo:
        query += " WHERE modelo = ?"
        params.append(filtro_modelo)
    query += " GROUP BY nivel_parecer ORDER BY nivel_parecer"
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()

def contar_por_area(filtro_modelo=None):
    query = "SELECT area_especialidade, COUNT(*) as total FROM analises"
    params = []
    if filtro_modelo:
        query += " WHERE modelo = ?"
        params.append(filtro_modelo)
    query += " GROUP BY area_especialidade ORDER BY total DESC"
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()

def listar_modelos_usados():
    with get_connection() as conn:
        rows = conn.execute("SELECT DISTINCT modelo FROM analises WHERE modelo IS NOT NULL").fetchall()
    return [r[0] for r in rows]


