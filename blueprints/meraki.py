import os
from flask import Blueprint, render_template, abort, url_for, redirect, session, request, flash
from jinja2 import TemplateNotFound


meraki = Blueprint('meraki', __name__,
                    template_folder='templates',
                    static_folder='static'
)


@meraki.route('/')
def index():
    session['base_grant_url'] = request.args.get('base_grant_url')
    session['user_continue_url'] = request.args.get('user_continue_url')
    session['node_mac'] = request.args.get('node_mac')
    session['client_ip'] = request.args.get('client_ip')
    session['client_mac'] = request.args.get('client_mac')
    session['merchant_id'] = request.args.get('merchant_id')
    return render_template('meraki-index.html')


@meraki.route('/callback')
def callback():
    if not session.get('user_id'):
        return redirect(url_for('meraki.index'))

    base_grant_url = session.get('base_grant_url')
    if not base_grant_url:
        flash('Failed to redirect to Meraki access point')
        return redirect(url_for('meraki.index'))

    callback = base_grant_url + "?continue_url=" + url_for('meraki.success')
    return redirect(callback)


@meraki.route('/success')
def success():
    if not session.get('user_id'):
        return redirect(url_for('meraki.index'))

    return render_template('meraki-success.html')

    