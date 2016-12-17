from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

common = Blueprint('common', __name__,
                        template_folder='templates',
                        static_folder='static')


@common.route('/')
def index():
    return render_template('index.html')


@common.route('/status/api')
def status_api():
    return 'OK'