from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Secret key for session management
DB_FILE = "users.db"

# Initialize Database
def init_db():
    print("[INFO] Initializing Database...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT UNIQUE, 
                password TEXT, 
                firstname TEXT, 
                lastname TEXT, 
                email TEXT UNIQUE, 
                address TEXT)''')
    conn.commit()
    conn.close()
    print("[INFO] Database Initialized Successfully!")

# Run Database Initialization
init_db()

@app.route('/')
def index():
    print("[INFO] Accessed Home Page")
    return render_template('home.html')

# ✅ Registration (Stores Plain Text Passwords) with Debug Logs
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        address = request.form['address']

        print(f"[INFO] Attempting to Register: {username}")

        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)",
                          (username, password, firstname, lastname, email, address))
                conn.commit()

            print(f"[SUCCESS] User {username} registered successfully!")
            session['user'] = username  # Store session
            return redirect(url_for('profile', username=username))

        except sqlite3.IntegrityError:
            print("[ERROR] Registration Failed - Username or Email already exists!")
            return "Username or Email already exists. Try again."

    print("[INFO] Rendering Registration Page")
    return render_template('register.html')

# ✅ Login (Uses Plain Text Passwords) with Debug Logs
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"[INFO] Attempting Login: {username}")

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()

        if user:
            print(f"[SUCCESS] Login Successful for {username}")
            session['user'] = username  # Store session
            return redirect(url_for('profile', username=username))
        else:
            print("[ERROR] Login Failed - Invalid Username or Password")
            return "Invalid username or password. Try again."

    print("[INFO] Rendering Login Page")
    return render_template('login.html')

@app.route('/logout')
def logout():
    print(f"[INFO] Logging out user: {session.get('user')}")
    session.pop('user', None)
    return redirect(url_for('index'))

# ✅ Profile Page Debugging
@app.route('/profile/<username>')
def profile(username):
    if 'user' not in session:
        print("[ERROR] Unauthorized Access Attempt to Profile")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    print(f"[INFO] Fetching Profile for: {username}")

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

    if user:
        print(f"[SUCCESS] Profile Loaded for {username}")
    else:
        print("[ERROR] Profile Not Found!")

    return render_template('profile.html', user=user)

if __name__ == '__main__':
    print("[INFO] Starting Flask Server...")
    app.run(debug=True)
