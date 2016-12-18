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

twitter = oauth.remote_app(
    'twitter',
    app_key='TWITTER',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize'
)

instagram = oauth.remote_app(
    'instagram',
    app_key='INSTAGRAM',
    base_url='https://api.instagram.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.instagram.com/oauth/access_token',
    authorize_url='https://api.instagram.com/oauth/authorize',
)

weibo = oauth.remote_app(
    'weibo',
    app_key='WEIBO',
    request_token_params={'scope': 'email,statuses_to_me_read'},
    base_url='https://api.weibo.com/2/',
    authorize_url='https://api.weibo.com/oauth2/authorize',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.weibo.com/oauth2/access_token',

    # force to parse the response in applcation/json
    content_type='application/json',
)

def change_weibo_header(uri, headers, body):
    auth = headers.get('Authorization')
    if auth:
        auth = auth.replace('Bearer', 'OAuth2')
        headers['Authorization'] = auth
    return uri, headers, body

weibo.pre_request = change_weibo_header


@oauth.invalid_response
def invalid_require_oauth(req):
    print 'Recieved invalid response', req.error_message
    return req.error_message, 401


@facebook.tokengetter
@twitter.tokengetter
@instagram.tokengetter
@weibo.tokengetter
def get_session():
    return session.get('tokens')

def reset_session():
    session.pop('network', None)
    session.pop('tokens', None)
    
def set_session(network, token, token_secret):
    session['network'] = network
    session['tokens'] = (token, token_secret)
    
def get_callback(route):
    return url_for(
        route,
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )



@auth.route('/facebook')
def facebook_login():
    return facebook.authorize(callback=get_callback('auth.facebook_authorized'))

@auth.route('/facebook/callback')
def facebook_authorized():
    resp = facebook.authorized_response()

    print 'Instagram authorized response', resp

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message

    set_session('facebook', resp['access_token'], '')

    me = facebook.get('/me')
    return 'Logged in as me=%s resp=%s redirect=%s' % (me, resp, request.args.get('next'))



@auth.route('/twitter')
def twitter_login():
    return twitter.authorize(callback=get_callback('auth.twitter_authorized'))

@auth.route('/twitter/callback')
def twitter_authorized():
    resp = twitter.authorized_response()

    print 'Twitter authorized response', resp

    if resp is None:
        return 'Access denied resp=%s' % resp

    set_session('twitter', resp['token'], resp['token_secret'])

    return 'Logged in as me=%s resp=%s redirect=%s' % ('', resp, request.args.get('next'))



@auth.route('/instagram')
def instagram_login():
    return instagram.authorize(callback=get_callback('auth.instagram_authorized'))

@auth.route('/instagram/callback')
def instagram_authorized():
    resp = instagram.authorized_response()

    print 'Instagram authorized response', resp

    if resp is None:
        return 'Access denied resp=%s' % resp

    set_session('instagram', resp.token, resp.token_secret)

    return 'Logged in as me=%s resp=%s redirect=%s' % ('', resp, request.args.get('next'))



@auth.route('/weibo')
def weibo_login():
    return weibo.authorize(callback=get_callback('auth.weibo_authorized'))

@auth.route('/weibo/callback')
def weibo_authorized():
    resp = weibo.authorized_response()

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    set_session('weibo', resp['access_token'], '')

    return 'Logged in as me=%s resp=%s redirect=%s' % ('', resp, request.args.get('next'))