import os
from flask import Blueprint, render_template, abort, url_for, redirect
from jinja2 import TemplateNotFound

common = Blueprint('common', __name__,
                        template_folder='templates',
                        static_folder='static')


@common.route('/')
def index():
    return render_template('index.html')


@common.route('/ok')
def status_api():
    # ELB health check endpoint - not logged in nginx or uwsgi
    return 'OK'


@common.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))
