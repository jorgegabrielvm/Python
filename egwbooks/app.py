from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from top10books import get_top_10_books


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a real secret key

DATABASE_PATH = 'dags/'  # Path to the 'dags' folder

######################################## SHOW BOOKS ##############################################

def get_books(query=None):
    conn = sqlite3.connect(f'{DATABASE_PATH}egw.db')
    cursor = conn.cursor()
    if query:
        cursor.execute('SELECT title, image_url, description FROM Books WHERE title LIKE ?', ('%' + query + '%',))
    else:
        cursor.execute('SELECT title, image_url, description FROM Books')
    books = cursor.fetchall()
    conn.close()
    return books


################################### USERS LOGIC #########################################

def add_user(username, email, password):
    conn = sqlite3.connect(f'{DATABASE_PATH}users.db')
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username or email already exists
    conn.close()
    return True

def authenticate_user(username, password):
    conn = sqlite3.connect(f'{DATABASE_PATH}users.db')
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user


###################################### LOGIN AND REGISTER #########################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticate_user(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('user'))
        else:
            return "Invalid username or password", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return "Passwords do not match", 400  # Handle password mismatch
        
        if add_user(username, email, password):
            return render_template('success.html')
        else:
            return "Username or email already exists", 400
    
    return render_template('register.html')



####################################### BASIC ROUTES ############################################

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('user'))
    return render_template('index.html', books=get_books(), search_query='')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/user')
def user():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('user.html', books=get_books(), search_query='')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


##################################### SEARCHS #################################################

@app.route('/search_index', methods=['GET'])
def search_index():
    if 'username' in session:
        return redirect(url_for('user'))
    query = request.args.get('search', '')
    books = get_books(query)
    return render_template('index.html', books=books, search_query=query)

@app.route('/search_user', methods=['GET'])
def search_user():
    if 'username' not in session:
        return redirect(url_for('index'))
    query = request.args.get('search', '')
    books = get_books(query)
    return render_template('user.html', books=books, search_query=query)


########################################### ORDERS #################################################


@app.route('/add_order', methods=['POST'])
def add_order():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    title = request.form['title']
    image_url = request.form['image_url']
    quantity = request.form['quantity']
    cover_type = request.form['cover_type']
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H:%M:%S')
    price = 7.99  # Default price

    conn = sqlite3.connect(f'{DATABASE_PATH}orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (username, title, image_url, quantity, cover_type, date, time, paid, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'no', ?)
    ''', (username, title, image_url, quantity, cover_type, date, time, price))
    conn.commit()
    conn.close()

    return redirect(url_for('orders'))


@app.route('/order/<book_title>')
def order(book_title):
    promotion = request.args.get('promotion', 'false') == 'true'
    
    conn = sqlite3.connect(f'{DATABASE_PATH}egw.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, image_url, description FROM Books WHERE title = ?', (book_title,))
    book = cursor.fetchone()
    conn.close()

    if book:
        book = {'title': book[0], 'image_url': book[1], 'description': book[2]}
        return render_template('order.html', book=book, promotion=promotion)
    
    return "Book not found", 404


############################################## FINAL (ORDERS) ######################################################

@app.route('/orders')
def orders():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    conn = sqlite3.connect(f'{DATABASE_PATH}orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, quantity, cover_type, date, time, paid, price
        FROM orders
        WHERE username = ? AND paid = 'no'
    ''', (username,))
    orders = cursor.fetchall()
    conn.close()
    
    orders_list = []
    total_price = 0
    for order in orders:
        price = float(order[7]) * float(order[2])  # Use the price from the database
        orders_list.append({
            'id': order[0],
            'title': order[1],
            'quantity': order[2],
            'cover_type': order[3],
            'date': order[4],
            'time': order[5],
            'price': price,
            'paid': order[6]
        })
        total_price += price
    
    return render_template('final.html', orders=orders_list, total_price=total_price)

@app.route('/pay', methods=['POST'])
def pay():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    conn = sqlite3.connect(f'{DATABASE_PATH}orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE orders
        SET paid = 'yes'
        WHERE username = ? AND paid = 'no'
    ''', (username,))
    conn.commit()
    conn.close()
    
    return render_template('confirmation.html')

@app.route('/delete_order', methods=['POST'])
def delete_order():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    order_id = request.form['order_id']
    print(f"Attempting to delete order with id: {order_id}")  # Debugging line
    
    conn = sqlite3.connect(f'{DATABASE_PATH}orders.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orders WHERE id = ? AND paid = "no"', (order_id,))
    conn.commit()
    conn.close()
    
    print(f"Order with id: {order_id} deleted.")  # Debugging line
    
    return redirect(url_for('orders'))

########################################## PROMO BOOKS #############################################

@app.route('/promo_order/<book_title>')
def promo_order(book_title):
    conn = sqlite3.connect(f'{DATABASE_PATH}egw.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, image_url, description FROM Books WHERE title = ?', (book_title,))
    book = cursor.fetchone()
    conn.close()

    if book:
        book = {'title': book[0], 'image_url': book[1], 'description': book[2]}
        return render_template('promo_book.html', book=book)
    
    return "Book not found", 404

@app.route('/add_promo_order', methods=['POST'])
def add_promo_order():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    title = request.form['title']
    image_url = request.form['image_url']
    quantity = request.form['quantity']
    cover_type = request.form['cover_type']
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H:%M:%S')
    promotional_price = 5.59

    conn = sqlite3.connect(f'{DATABASE_PATH}orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (username, title, image_url, quantity, cover_type, date, time, paid, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'no', ?)
    ''', (username, title, image_url, quantity, cover_type, date, time, promotional_price))
    conn.commit()
    conn.close()

    return redirect(url_for('orders'))

######################################### FEEDBACK ##############################################

def init_feedback_db():
    conn = sqlite3.connect(f'{DATABASE_PATH}feedback.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY,
            username TEXT,
            category TEXT,
            rating INTEGER,
            feedback TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize feedback database
init_feedback_db()


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['username']
        category = request.form['category']
        rating = int(request.form['rating'])
        feedback_text = request.form['feedback']

        # Log the feedback details
        print(f'Received feedback: {username}, {category}, {rating}, {feedback_text}')

        # Insert feedback into feedback.db
        conn = sqlite3.connect(f'{DATABASE_PATH}feedback.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO feedback (username, category, rating, feedback)
            VALUES (?, ?, ?, ?)
        ''', (username, category, rating, feedback_text))
        conn.commit()
        conn.close()

        return render_template('thank_you.html')

    return render_template('feedback.html')


######################################## TOP 10 BOOKS ############################################################

@app.route('/top10')
def top10():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    top_10_books = get_top_10_books()
    return render_template('top10books.html', books=top_10_books)



####################################################### PROMOTIONS #################################################################

# ML Algo code using Cosine Similarity

@app.route('/promotions')
def promotions():
    username = session.get('username', 'Guest')  # Get current user's username from the session
    default_price = 7.99

    # Connect to the orders database
    conn_orders = sqlite3.connect(f'{DATABASE_PATH}orders.db')

    # Load data from the orders table
    orders_df = pd.read_sql_query("SELECT * FROM orders", conn_orders)

    # Close the orders database connection
    conn_orders.close()

    # Connect to the books database
    conn_books = sqlite3.connect(f'{DATABASE_PATH}egw.db')

    # Load data from the Books table
    books_df = pd.read_sql_query("SELECT * FROM Books", conn_books)

    # Close the books database connection
    conn_books.close()

    # Get the books purchased by the current user
    user_books = orders_df[orders_df['username'] == username]['title'].unique()

    if len(user_books) == 0:
        return render_template('promotions.html', books=[])

    # Create a DataFrame for the books and their attributes
    unique_books_df = books_df.drop_duplicates(subset=['title']).set_index('title')

    # Create a pivot table for similarity calculation
    pivot_table = orders_df.pivot_table(index='title', columns='id', values='quantity', fill_value=0)

    # Create a similarity matrix
    similarity_matrix = cosine_similarity(pivot_table)

    # Convert the similarity matrix to a DataFrame
    similarity_df = pd.DataFrame(similarity_matrix, index=pivot_table.index, columns=pivot_table.index)

    # Get the top 5 similar books for each book purchased by the user
    recommended_books = set()
    for book in user_books:
        if book in similarity_df:
            similar_books = similarity_df[book].sort_values(ascending=False).index[1:6].tolist()
            recommended_books.update(similar_books)

    # Remove the books already purchased by the user
    recommended_books.difference_update(user_books)
    recommended_books = list(recommended_books)[:10]

    # Query the recommended books' details from the unique books DataFrame
    recommended_books_details = unique_books_df.loc[recommended_books, ['image_url', 'description']].to_dict('index')

    # Add fixed price and discounted prices
    for book, details in recommended_books_details.items():
        details['price'] = default_price
        details['discounted_price'] = 5.59

    # Render the promotions page
    return render_template('promotions.html', books=recommended_books_details.items())




if __name__ == '__main__':
    app.run(debug=True)
