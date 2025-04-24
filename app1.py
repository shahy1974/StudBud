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

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('ask.html')

    data = request.get_json()
    question = data.get('question')

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        "model": "deepseek-chat",  # You can replace this with the exact model you want
        "messages": [
            {"role": "user", "content": question}
        ]
    }

    response = requests.post("https://api.deepseek.com/v1/chat/completions", json=payload, headers=headers)

    if response.status_code == 200:
        ai_answer = response.json()["choices"][0]["message"]["content"]
        return jsonify({"answer": ai_answer})
    else:
        return jsonify({"answer": "Error fetching answer from AI."})

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
