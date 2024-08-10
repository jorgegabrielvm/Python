import sqlite3

def add_promotion_column():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()

    # Check if the 'promotion' column exists
    cursor.execute("PRAGMA table_info(orders)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'promotion' not in columns:
        # Add the 'promotion' column
        cursor.execute('ALTER TABLE orders ADD COLUMN promotion TEXT DEFAULT \'no\'')
        conn.commit()

    conn.close()

if __name__ == "__main__":
    add_promotion_column()
    print("Database updated successfully.")
