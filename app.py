from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime
from models import db, Log

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # or your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create tables (run this once to create the database)
with app.app_context():
    db.create_all()

# Database config - change these to your actual db info
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Root@7x!pl9',
    'database': 'soil_fertility'
}

# Home dashboard
@app.route('/')
def dashboard():
    embed_url = "https://app.powerbi.com/view?r=eyJrIjoiYWU2Y2NiNWMtNDE2OS00MTc4LThjYTYtZjllY2E2NDU4NTBlIiwidCI6ImNkY2JiMGUyLTlmZWEtNGY1NC04NjcwLTY3MjcwNzc5N2FkYSIsImMiOjEwfQ%3D%3D"
    return render_template('dashboard.html', embed_url=embed_url)

# About us page
@app.route('/about_us')
def about_us():
    map_embed_url = "https://app.powerbi.com/view?r=eyJrIjoiNGEwZjIwY2ItZTcxNi00NDBiLWI0ZTAtYzQ1OGMxMmJmNDFkIiwidCI6ImNkY2JiMGUyLTlmZWEtNGY1NC04NjcwLTY3MjcwNzc5N2FkYSIsImMiOjEwfQ%3D%3D"
    return render_template('about_us.html', map_embed_url=map_embed_url)

# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Register new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
            conn.commit()
            flash("Registration successful. Please login.")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash("Username already exists.")
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

# Login user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            flash("Login successful.")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
    return render_template('login.html')

# Logout user
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

# View all fertilizer logs
@app.route('/fertilizer_log')
def fertilizer_log():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fertilizer_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('fertilizer_log.html', logs=logs)

# Add a new log
@app.route('/add_log', methods=['GET', 'POST'])
def add_log():
    if request.method == 'POST':
        nutrient = request.form['nutrient']
        amount = request.form['amount']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fertilizer_logs (nutrient_type, amount_added) VALUES (%s, %s)", (nutrient, amount))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Log added successfully!")
        return redirect(url_for('fertilizer_log'))
    return render_template('edit_log.html', log=None)

# Edit a log
@app.route('/edit_log/<int:log_id>', methods=['GET', 'POST'])
def edit_log(log_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        nutrient = request.form['nutrient']
        amount = request.form['amount']
        cursor.execute("UPDATE fertilizer_logs SET nutrient_type=%s, amount_added=%s WHERE id=%s", (nutrient, amount, log_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Log updated successfully!")
        return redirect(url_for('fertilizer_log'))

    cursor.execute("SELECT * FROM fertilizer_logs WHERE id = %s", (log_id,))
    log = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_log.html', log=log)

# Delete a log
@app.route('/delete_log/<int:log_id>')
def delete_log(log_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fertilizer_logs WHERE id = %s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Log deleted successfully!")
    return redirect(url_for('fertilizer_log'))

if __name__ == '__main__':
    app.run(debug=True)