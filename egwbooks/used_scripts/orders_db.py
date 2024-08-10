import sqlite3

conn = sqlite3.connect('orders.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    title TEXT NOT NULL,
    image_url TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    cover_type TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    paid TEXT NOT NULL DEFAULT 'no'
)
''')

conn.commit()
conn.close()
