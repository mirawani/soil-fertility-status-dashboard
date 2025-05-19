from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure this to your needs
ITEMS_PER_PAGE = 10

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Root@7x!pl9',
    'database': 'soil_fertility'
}

# Home Dashboard
@app.route('/')
def dashboard():
    embed_url = "https://app.powerbi.com/view?r=eyJrIjoiYWU2Y2NiNWMtNDE2OS00MTc4LThjYTYtZjllY2E2NDU4NTBlIiwidCI6ImNkY2JiMGUyLTlmZWEtNGY1NC04NjcwLTY3MjcwNzc5N2FkYSIsImMiOjEwfQ%3D%3D"
    return render_template('dashboard.html', embed_url=embed_url)


# About Us
@app.route('/about-us')
def about_us():
    map_embed_url = "https://app.powerbi.com/view?r=eyJrIjoiNGEwZjIwY2ItZTcxNi00NDBiLWI0ZTAtYzQ1OGMxMmJmNDFkIiwidCI6ImNkY2JiMGUyLTlmZWEtNGY1NC04NjcwLTY3MjcwNzc5N2FkYSIsImMiOjEwfQ%3D%3D"
    return render_template('about_us.html', map_embed_url=map_embed_url)

# Contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Register
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

# Login
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

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

# Fertilizer Log (with pagination and search)
@app.route('/fertilizer_log')
def fertilizer_log():
    if 'user_id' not in session:
        flash("Please log in to view your fertilizer logs.")
        return render_template('fertilizer_log.html', logs=None, pagination=None)

    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    search_date = request.args.get('search_date', '')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Base query
    query = "SELECT * FROM fertilizer_logs WHERE user_id = %s"
    params = [user_id]

    # Add date filter if provided
    if search_date:
        try:
            # Validate date format
            datetime.strptime(search_date, '%Y-%m-%d')
            query += " AND DATE(timestamp) = %s"
            params.append(search_date)
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect(url_for('fertilizer_log'))

    # Count total records for pagination
    count_query = "SELECT COUNT(*) as total FROM fertilizer_logs WHERE user_id = %s"
    count_params = [user_id]
    if search_date:
        count_query += " AND DATE(timestamp) = %s"
        count_params.append(search_date)

    cursor.execute(count_query, count_params)
    total = cursor.fetchone()['total']
    total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    # Add ordering and pagination
    query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
    params.extend([ITEMS_PER_PAGE, (page - 1) * ITEMS_PER_PAGE])

    cursor.execute(query, params)
    logs = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'fertilizer_log.html',
        logs=logs,
        pagination={
            'page': page,
            'per_page': ITEMS_PER_PAGE,
            'total': total,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1,
            'next_num': page + 1,
            'iter_pages': lambda: range(1, total_pages + 1)
        },
        search_date=search_date
    )

# Add New Log
@app.route('/add_log', methods=['GET', 'POST'])
def add_log():
    if 'user_id' not in session:
        flash("Please log in to add a fertilizer log.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        nutrient = request.form['nutrient']
        amount = request.form['amount']
        user_id = session['user_id']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO fertilizer_logs (nutrient_type, amount_added, user_id) VALUES (%s, %s, %s)",
            (nutrient, amount, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Log added successfully!")
        return redirect(url_for('fertilizer_log'))
    return render_template('edit_log.html', log=None)

# Edit Log
@app.route('/edit_log/<int:log_id>', methods=['GET', 'POST'])
def edit_log(log_id):
    if 'user_id' not in session:
        flash("Please log in to edit fertilizer logs.")
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Check ownership
    cursor.execute("SELECT * FROM fertilizer_logs WHERE id = %s AND user_id = %s", (log_id, user_id))
    log = cursor.fetchone()
    if not log:
        flash("You do not have permission to edit this log.")
        return redirect(url_for('fertilizer_log'))

    if request.method == 'POST':
        nutrient = request.form['nutrient']
        amount = request.form['amount']
        cursor.execute(
            "UPDATE fertilizer_logs SET nutrient_type=%s, amount_added=%s WHERE id=%s",
            (nutrient, amount, log_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Log updated successfully!")
        return redirect(url_for('fertilizer_log'))

    cursor.close()
    conn.close()
    return render_template('edit_log.html', log=log)

# Delete Log
@app.route('/delete_log/<int:log_id>')
def delete_log(log_id):
    if 'user_id' not in session:
        flash("Please log in to delete fertilizer logs.")
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Ensure user owns the log
    cursor.execute("SELECT * FROM fertilizer_logs WHERE id = %s AND user_id = %s", (log_id, user_id))
    if cursor.fetchone() is None:
        flash("You do not have permission to delete this log.")
        return redirect(url_for('fertilizer_log'))

    cursor.execute("DELETE FROM fertilizer_logs WHERE id = %s", (log_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Log deleted successfully!")
    return redirect(url_for('fertilizer_log'))

if __name__ == '__main__':
    app.run(debug=True)