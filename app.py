import sqlite3
from flask import Flask, request, session, redirect, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT UNIQUE NOT NULL,
         password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

create_users_table()

@app.route('/')
def home():
    if 'username' in session:
        return f"Welcome, {session['username']}! <a href='/logout'>Logout</a>"
    return "You are not logged in. <a href='/login'>Login</a> | <a href='/register'>Register</a>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
       hashed_password = generate_password_hash(password)

       conn = get_db_connection()
       try:
           conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                        (username, hashed_password))
           conn.commit()
           flash('Registration successful! Please log in.')
           return redirect('/login')
       except sqlite3.IntegrityError:
           flash('Username already exists.')
           return redirect('/register')
       finally:
           conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
  
       conn = get_db_connection()
       user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
       conn.close()

       if user and check_password_hash(user['password'], password):
          session['username'] = user['username']
          return redirect('/')
       else:
          flash('Invalid username or password.')
          return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
     session.pop('username', None)
     return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
