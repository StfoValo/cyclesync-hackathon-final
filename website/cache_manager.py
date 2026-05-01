import sqlite3
import json
import os

CACHE_DB_PATH = os.path.join(os.path.dirname(__file__), "ui_cache.db")

def init_db():
    conn = sqlite3.connect(CACHE_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS api_cache (
            endpoint_key TEXT PRIMARY KEY,
            json_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def set_cache(key: str, data: dict):
    conn = sqlite3.connect(CACHE_DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO api_cache (endpoint_key, json_data)
        VALUES (?, ?)
    ''', (key, json.dumps(data)))
    conn.commit()
    conn.close()

def get_cache(key: str) -> dict:
    conn = sqlite3.connect(CACHE_DB_PATH)
    c = conn.cursor()
    c.execute('SELECT json_data FROM api_cache WHERE endpoint_key = ?', (key,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None
