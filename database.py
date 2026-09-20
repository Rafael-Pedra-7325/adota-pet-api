import sqlite3
from contextlib import contextmanager

DB_PATH = "pets.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    especie TEXT NOT NULL,
    idade_meses INTEGER,
    porte TEXT NOT NULL CHECK (porte IN ('pequeno', 'medio', 'grande')),
    descricao TEXT,
    status TEXT NOT NULL DEFAULT 'disponivel' CHECK (status IN ('disponivel', 'adotado')),
    adotante TEXT
);
"""


@contextmanager
def get_connection(db_path=None):
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path=None, seed=False):
    if db_path is None:
        db_path = DB_PATH
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)
        if seed:
            existentes = conn.execute("SELECT COUNT(*) FROM pets").fetchone()[0]
            if existentes == 0:
                conn.executemany(
                    "INSERT INTO pets (nome, especie, idade_meses, porte, descricao) VALUES (?, ?, ?, ?, ?)",
                    [
                        ("Toby", "cachorro", 18, "medio", "Dócil e brincalhão, adora crianças."),
                        ("Mia", "gato", 8, "pequeno", "Independente, gosta de dormir no sol."),
                        ("Thor", "cachorro", 36, "grande", "Muito protetor, já sabe sentar e dar a pata."),
                    ],
                )
