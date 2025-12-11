import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_text TEXT NOT NULL,
        title TEXT NOT NULL,
        priority TEXT CHECK (priority IN ('High', 'Medium', 'Low')) DEFAULT 'Medium',
        deadline TEXT ,
        category TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    """
)

