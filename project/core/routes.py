from flask import Blueprint, render_template

core = Blueprint('core', __name__, template_folder='templates', static_folder='static', static_url_path='/')

@core.route('/')
def index():
    return render_template('core/index.html')