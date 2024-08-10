import sqlite3
import pandas as pd

DATABASE_PATH = 'dags/'

def get_top_10_books():
    """
    Retrieve the top 10 best-selling books based on the total quantity sold.
    """
    conn_orders = sqlite3.connect(f'{DATABASE_PATH}orders.db')
    orders_df = pd.read_sql_query("SELECT title, quantity FROM orders", conn_orders)
    conn_orders.close()

    # Aggregate the quantities sold for each book title
    book_sales = orders_df.groupby('title')['quantity'].sum()

    # top 10 in order
    top_selling_books = book_sales.sort_values(ascending=False).head(10).index.tolist()

    # Fetch book details from the books database and
    # JOIN "top_selling_books"
    conn_books = sqlite3.connect(f'{DATABASE_PATH}egw.db')
    placeholders = ', '.join(['?'] * len(top_selling_books))
    query = f"SELECT title, image_url, description FROM Books WHERE title IN ({placeholders})"
    cursor = conn_books.cursor()
    cursor.execute(query, top_selling_books)
    top_10_books = cursor.fetchall()
    conn_books.close()

    # Convert the fetched data into a DataFrame
    top_10_books_df = pd.DataFrame(top_10_books, columns=['title', 'image_url', 'description'])

    # Reorder the DataFrame to match the order of `top_selling_books`
    top_10_books_df['title'] = pd.Categorical(top_10_books_df['title'], categories=top_selling_books, ordered=True)
    top_10_books_df = top_10_books_df.sort_values('title')

    # Convert the DataFrame back to a list of tuples to return
    top_10_books_list = top_10_books_df.to_records(index=False).tolist()

    return top_10_books_list

# Debugging Trick: The Desire Of Ages must be the first one
