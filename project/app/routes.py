from flask import Blueprint, render_template

app = Blueprint('app', __name__, template_folder='templates', static_folder='static', static_url_path='/')

@app.route('/')
def index():
    return render_template('app/index.html')