from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from flask import send_from_directory  # For serving static files

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # From .env file

# DeepSeek API Config (example, not used here yet)
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

users = {}  # Temporary user storage, replace with database in production

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
        return redirect(url_for('ask'))  # Redirect to 'ask' page
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

# This is the route to display the form and submit a question (GET and POST)
@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    
    if request.method == 'GET':
        # Show the ask form to the logged-in user
        return render_template('ask.html')
    
    # Handle the question submission (POST request)
    question = request.form.get('question')  # Get the question from the form
    # Here, you can process the question as needed
    # Placeholder response - you can modify this with actual logic or API call
    answer = f"You asked: {question}"
    
    return jsonify({"answer": answer})  # Returning the answer as a JSON response

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# Static files route (if needed for serving assets like CSS, JS, images)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
