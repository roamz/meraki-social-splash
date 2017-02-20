import os
from flask import Blueprint, render_template, abort, url_for, redirect, session, request, flash, current_app
from jinja2 import TemplateNotFound


meraki = Blueprint('meraki', __name__,
                    template_folder='templates',
                    static_folder='static'
)

@meraki.route('/<merchant_id>')
@meraki.route('/<merchant_id>/<place_name>')
def index(merchant_id, place_name=None):
    session['merchant_id'] = merchant_id
    session['asset_path'] = merchant_id + ('/' + place_name if place_name else '')
    session['base_grant_url'] = request.args.get('base_grant_url')
    session['user_continue_url'] = request.args.get('user_continue_url')
    session['node_mac'] = request.args.get('node_mac')
    session['client_ip'] = request.args.get('client_ip')
    session['client_mac'] = request.args.get('client_mac')
    return render_template('meraki-index.html')


@meraki.route('/callback')
def callback():
    if not session.get('user_id'):
        print '/meraki/callback user_id not in session'
        return redirect(url_for('meraki.index', merchant_id=session.get('merchant_id')))

    base_grant_url = session.get('base_grant_url')
    if not base_grant_url:
        print '/meraki/callback base_grant_url not in session'
        flash('Failed to redirect to Meraki access point')
        return redirect(url_for('meraki.index', merchant_id=session.get('merchant_id')))

    callback = base_grant_url + "?continue_url=" + url_for('meraki.success', _external=True)
    return redirect(callback)


@meraki.route('/success')
def success():
    if not session.get('user_id'):
        return redirect(url_for('meraki.index'))

    return render_template('meraki-success.html', lm_api_url=current_app.config['LOCALMEASURE_API_URL'])


