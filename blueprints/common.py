from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

common = Blueprint('common', __name__,
                        template_folder='templates',
                        static_folder='static')


@common.route('/')
def index():
    #try:
    return render_template('index.html')
    #except TemplateNotFound:
    #    abort(404)

