from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # From .env file

# DeepSeek API Config
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

users = {}  # Temporary user storage,replace with database in production

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username in users and check_password_hash(users[username]['password'], password):
        session['username'] = username
        return redirect(url_for('ask'))  # Redirect to ask page
    return render_template('login.html', error="Invalid credentials")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    # Handle POST request
    username = request.form.get('username')
    if username in users:
        return render_template('signup.html', error="Username already exists")
    
    users[username] = {
        'password': generate_password_hash(request.form.get('password')),
        'email': request.form.get('email')
    }
    return redirect(url_for('login'))  # Redirect to login page

@app.route('/ask', methods=['POST'])
def answer_question():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    question = data.get("question")
    # Placeholder response
    return jsonify({"answer": f"You asked: {question}"})



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# Static files route
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)