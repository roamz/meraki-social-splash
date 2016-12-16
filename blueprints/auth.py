from flask_oauthlib.client import OAuth, OAuthException
from flask import Blueprint, request, g, url_for, session

auth = Blueprint('auth', __name__)

oauth = OAuth()

facebook = oauth.remote_app(
    'facebook',
    app_key='FACEBOOK',
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    access_token_method='GET',
    authorize_url='https://www.facebook.com/dialog/oauth'
)

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@auth.route('/facebook')
def facebook_login():
    callback = url_for(
        'auth.facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return facebook.authorize(callback=callback)

@auth.route('/facebook/callback')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    return 'Logged in as id=%s name=%s email=%s redirect=%s' % \
        (me.data['id'], me.data['name'], me.data['email'], request.args.get('next'))


