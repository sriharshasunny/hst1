import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_db():
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('data/foodexpress.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        phone TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount REAL,
        status TEXT,
        payment_method TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create order_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        item_name TEXT,
        quantity INTEGER,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username, email, password, full_name=None, phone=None, address=None):
    conn = sqlite3.connect('data/foodexpress.db')
    c = conn.cursor()
    
    try:
        hashed_password = generate_password_hash(password)
        c.execute('''INSERT INTO users (username, email, password, full_name, phone, address)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (username, email, hashed_password, full_name, phone, address))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('data/foodexpress.db')
    c = conn.cursor()
    
    c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        return user[0]  # Return user ID
    return None

def get_user_by_id(user_id):
    conn = sqlite3.connect('data/foodexpress.db')
    c = conn.cursor()
    
    c.execute('SELECT id, username, email, full_name, phone, address FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[3],
            'phone': user[4],
            'address': user[5]
        }
    return None

def update_user_profile(user_id, full_name=None, phone=None, address=None):
    conn = sqlite3.connect('data/foodexpress.db')
    c = conn.cursor()
    
    try:
        c.execute('''UPDATE users 
                    SET full_name = COALESCE(?, full_name),
                        phone = COALESCE(?, phone),
                        address = COALESCE(?, address)
                    WHERE id = ?''',
                 (full_name, phone, address, user_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def create_order(user_id, items, total_amount, payment_method):
    conn = sqlite3.connect('data/foodexpress.db')
    c = conn.cursor()
    
    try:
        c.execute('''INSERT INTO orders (user_id, total_amount, status, payment_method)
                    VALUES (?, ?, 'pending', ?)''',
                 (user_id, total_amount, payment_method))
        order_id = c.lastrowid
        
        for item in items:
            c.execute('''INSERT INTO order_items (order_id, item_name, quantity, price)
                        VALUES (?, ?, ?, ?)''',
                     (order_id, item['name'], item['quantity'], item['price']))
        
        conn.commit()
        return order_id
    except:
        return None
    finally:
        conn.close()

def get_user_orders(user_id):
    conn = sqlite3.connect('data/foodexpress.db')
    c = conn.cursor()
    
    c.execute('''SELECT o.id, o.order_date, o.total_amount, o.status, o.payment_method,
                        GROUP_CONCAT(oi.item_name || ' x' || oi.quantity)
                 FROM orders o
                 LEFT JOIN order_items oi ON o.id = oi.order_id
                 WHERE o.user_id = ?
                 GROUP BY o.id
                 ORDER BY o.order_date DESC''', (user_id,))
    
    orders = c.fetchall()
    conn.close()
    
    return [{
        'id': order[0],
        'date': order[1],
        'total': order[2],
        'status': order[3],
        'payment_method': order[4],
        'items': order[5]
    } for order in orders]

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!") 