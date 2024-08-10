import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('orders.db')
cursor = conn.cursor()

# Add the price column with a default value of 7.99
cursor.execute('ALTER TABLE orders ADD COLUMN price REAL DEFAULT 7.99')

# Update existing rows to have the default price
cursor.execute('UPDATE orders SET price = 7.99 WHERE price IS NULL')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Price column added successfully and default value set to 7.99 for existing rows.")
