import os
from flask import Blueprint, render_template, abort, url_for, redirect, session
from jinja2 import TemplateNotFound
from auth import del_user

common = Blueprint('common', __name__,
                        template_folder='templates',
                        static_folder='static')


@common.route('/')
def index():
    return render_template('index.html')


@common.route('/logout')
def logout():
    del_user()
    return redirect(url_for('common.index'))


@common.route('/ok')
def status_api():
    # ELB health check endpoint - not logged in nginx or uwsgi
    return 'OK'


@common.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))




@common.route('/meraki')
def meraki_login():
    return render_template('meraki.html')


@common.route('/meraki/success')
def meraki_success():
    # ELB health check endpoint - not logged in nginx or uwsgi
    return 'OK'