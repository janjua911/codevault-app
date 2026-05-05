from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
import os
import hashlib
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'codevault-secret-key-2026'
DATABASE = 'codevault.db'

# ─── Database ────────────────────────────────────────────────────────────────

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                language TEXT NOT NULL,
                description TEXT,
                code TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')
        db.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─── Auth decorator ──────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    query = request.args.get('q', '')
    lang = request.args.get('lang', '')
    sql = '''SELECT s.*, u.username FROM snippets s
             JOIN users u ON s.user_id = u.id WHERE 1=1'''
    params = []
    if query:
        sql += ' AND (s.title LIKE ? OR s.description LIKE ?)'
        params += [f'%{query}%', f'%{query}%']
    if lang:
        sql += ' AND s.language = ?'
        params.append(lang)
    sql += ' ORDER BY s.created_at DESC'
    snippets = db.execute(sql, params).fetchall()
    languages = db.execute('SELECT DISTINCT language FROM snippets ORDER BY language').fetchall()
    return render_template('index.html', snippets=snippets, languages=languages, query=query, lang=lang)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm', '')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        db = get_db()
        try:
            db.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                       [username, email, hash_password(password)])
            db.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                          [username, hash_password(password)]).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/snippet/<int:sid>')
def view_snippet(sid):
    db = get_db()
    snippet = db.execute('''SELECT s.*, u.username FROM snippets s
                            JOIN users u ON s.user_id = u.id WHERE s.id = ?''', [sid]).fetchone()
    if not snippet:
        flash('Snippet not found.', 'error')
        return redirect(url_for('index'))
    return render_template('view.html', snippet=snippet)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_snippet():
    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        language = request.form.get('language', '').strip()
        desc     = request.form.get('description', '').strip()
        code     = request.form.get('code', '').strip()

        if not title or not language or not code:
            flash('Title, language, and code are required.', 'error')
            return render_template('add.html')

        db = get_db()
        db.execute('INSERT INTO snippets (title, language, description, code, user_id) VALUES (?,?,?,?,?)',
                   [title, language, desc, code, session['user_id']])
        db.commit()
        flash('Snippet saved to the vault!', 'success')
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:sid>', methods=['GET', 'POST'])
@login_required
def edit_snippet(sid):
    db = get_db()
    snippet = db.execute('SELECT * FROM snippets WHERE id = ? AND user_id = ?',
                         [sid, session['user_id']]).fetchone()
    if not snippet:
        flash('Snippet not found or access denied.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        language = request.form.get('language', '').strip()
        desc     = request.form.get('description', '').strip()
        code     = request.form.get('code', '').strip()

        if not title or not language or not code:
            flash('Title, language, and code are required.', 'error')
            return render_template('edit.html', snippet=snippet)

        db.execute('UPDATE snippets SET title=?, language=?, description=?, code=? WHERE id=?',
                   [title, language, desc, code, sid])
        db.commit()
        flash('Snippet updated!', 'success')
        return redirect(url_for('view_snippet', sid=sid))
    return render_template('edit.html', snippet=snippet)

@app.route('/delete/<int:sid>', methods=['POST'])
@login_required
def delete_snippet(sid):
    db = get_db()
    snippet = db.execute('SELECT * FROM snippets WHERE id = ? AND user_id = ?',
                         [sid, session['user_id']]).fetchone()
    if not snippet:
        flash('Snippet not found or access denied.', 'error')
    else:
        db.execute('DELETE FROM snippets WHERE id = ?', [sid])
        db.commit()
        flash('Snippet deleted from the vault.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    snippets = db.execute('SELECT * FROM snippets WHERE user_id = ? ORDER BY created_at DESC',
                          [session['user_id']]).fetchall()
    count = len(snippets)
    languages = db.execute('SELECT DISTINCT language FROM snippets WHERE user_id = ?',
                            [session['user_id']]).fetchall()
    return render_template('dashboard.html', snippets=snippets, count=count, languages=languages)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='13.206.54.52', port=5000)
