from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from database import init_db, create_user, verify_user, get_user_by_id, update_user_profile, create_order, get_user_orders

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user_id = verify_user(username, password)
    if user_id:
        session['user_id'] = user_id
        return jsonify({'success': True, 'redirect': '/index1'})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if create_user(username, email, password):
        return jsonify({'success': True, 'redirect': '/login'})
    else:
        return jsonify({'error': 'Username or email already exists'}), 400

@app.route('/api/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if request.method == 'GET':
        user = get_user_by_id(session['user_id'])
        if user:
            return jsonify(user)
        return jsonify({'error': 'User not found'}), 404
    
    elif request.method == 'POST':
        data = request.get_json()
        if update_user_profile(session['user_id'], 
                             data.get('full_name'),
                             data.get('phone'),
                             data.get('address')):
            return jsonify({'success': True})
        return jsonify({'error': 'Failed to update profile'}), 400

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login_page'))

@app.route('/index1')
def index1():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index1.html')

@app.route('/api/orders', methods=['GET', 'POST'])
def orders():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if request.method == 'GET':
        orders = get_user_orders(session['user_id'])
        return jsonify(orders)
    
    elif request.method == 'POST':
        data = request.get_json()
        items = data.get('items')
        total_amount = data.get('total_amount')
        payment_method = data.get('payment_method')
        
        if not all([items, total_amount, payment_method]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        order_id = create_order(session['user_id'], items, total_amount, payment_method)
        if order_id:
            return jsonify({'success': True, 'order_id': order_id})
        return jsonify({'error': 'Failed to create order'}), 400

if __name__ == '__main__':
    app.run(debug=True) 