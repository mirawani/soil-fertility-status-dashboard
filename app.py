import os
print(f"Current directory: {os.listdir()}")
print(f"Templates exists?: {'templates' in os.listdir()}")
print(f"Template files: {os.listdir('templates') if 'templates' in os.listdir() else 'No templates dir'}")

from flask import Flask, render_template, url_for

app = Flask(__name__)

# Route for the dashboard
@app.route('/')
def dashboard():
    embed_url = "https://app.powerbi.com/view?r=eyJrIjoiNzNkZmFjOWQtMjQ2ZS00MzFlLWFiNjYtYTgwMzFjMTExOTExIiwidCI6ImNkY2JiMGUyLTlmZWEtNGY1NC04NjcwLTY3MjcwNzc5N2FkYSIsImMiOjEwfQ%3D%3D"
    return render_template('dashboard.html', embed_url=embed_url)

# Route for About Us
@app.route('/about-us')
def about_us():
    map_embed_url = "https://app.powerbi.com/view?r=eyJrIjoiNGEwZjIwY2ItZTcxNi00NDBiLWI0ZTAtYzQ1OGMxMmJmNDFkIiwidCI6ImNkY2JiMGUyLTlmZWEtNGY1NC04NjcwLTY3MjcwNzc5N2FkYSIsImMiOjEwfQ%3D%3D"
    return render_template('about_us.html', map_embed_url=map_embed_url)

# Route for Contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)