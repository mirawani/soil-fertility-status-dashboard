import os
from flask import Flask, render_template

app = Flask(__name__)

# DEBUG: Print template paths
print(f"Current dir: {os.listdir()}")
print(f"Templates dir exists: {'templates' in os.listdir()}")
print(f"Files in templates/: {os.listdir('templates') if 'templates' in os.listdir() else 'MISSING'}")

# Route for the dashboard
@app.route('/')
def dashboard():
    embed_url = "https://app.powerbi.com/view?r=eyJrIjoiYWU2Y2NiNWMtNDE2OS00MTc4LThjYTYtZjllY2E2NDU4NTBlIiwidCI6ImNkY2JiMGUyLTlmZWEtNGY1NC04NjcwLTY3MjcwNzc5N2FkYSIsImMiOjEwfQ%3D%3D"
    return render_template('dashboard.html', embed_url=embed_url)

# Route for About Us
@app.route('/about_us')
def about_us():
    map_embed_url = "https://app.powerbi.com/view?r=eyJrIjoiNGEwZjIwY2ItZTcxNi00NDBiLWI0ZTAtYzQ1OGMxMmJmNDFkIiwidCI6ImNkY2JiMGUyLTlmZWEtNGY1NC04NjcwLTY3MjcwNzc5N2FkYSIsImMiOjEwfQ%3D%3D"
    return render_template('about_us.html', map_embed_url=map_embed_url)

# Route for Contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)