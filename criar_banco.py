import sqlite3
import os

# Garante que a pasta 'database' existe
os.makedirs('database', exist_ok=True)

# Conecta ao banco de dados
conn = sqlite3.connect('database/tarefas.db')
cursor = conn.cursor()

# Cria a tabela de tarefas
cursor.execute('''
CREATE TABLE IF NOT EXISTS tarefas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    concluida BOOLEAN NOT NULL DEFAULT 0
)
''')

conn.commit()
conn.close()

print("✅ Banco de dados criado com sucesso.")