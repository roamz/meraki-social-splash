from flask_oauthlib.client import OAuth, OAuthException
from flask import Blueprint, request, g, url_for, session, redirect, flash

INDEX = 'common.index'

auth = Blueprint('auth', __name__)

oauth = OAuth()

facebook = oauth.remote_app(
    'facebook',
    app_key='FACEBOOK',
    #request_token_params={'scope': 'email'},
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
    authorize_url='https://api.twitter.com/oauth/authenticate'
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



@facebook.tokengetter
@twitter.tokengetter
@instagram.tokengetter
@weibo.tokengetter
def get_tokens():
    return session.get('tokens')
    
def set_tokens(network, token, token_secret):
    session['network'] = network
    session['tokens'] = (token, token_secret)

def set_user(user_id, username=None, name=None, avatar=None):
    session['user_id'] = user_id
    if username: session['username'] = username
    if name:     session['name']     = name
    if avatar:   session['avatar']   = avatar

def reset_session():
    session.pop('network', None)
    session.pop('tokens', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('name', None)
    session.pop('avatar', None)

def get_callback(route):
    return url_for(
        route,
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )

def configured(remote_app):
    if remote_app.consumer_key and remote_app.consumer_secret:
        return True
    print 'ConfigError please configure environment variables for %s%s and %s%s' % (remote_app.app_key, remote_app.consumer_key, remote_app.app_key, remote_app.consumer_secret)
    flash('Unable to authorize you with %s because of a bad configuration, please try another method.' % remote_app.app_key.title())
    return False



@auth.route('/facebook')
def facebook_login():
    if not configured(facebook):
        return redirect(url_for(INDEX))
    return facebook.authorize(callback=get_callback('auth.facebook_authorized'))

@auth.route('/facebook/callback')
def facebook_authorized():
    try:
        resp = facebook.authorized_response()
    except OAuthException, e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Facebook: %s' % e.message)
        return redirect(url_for(INDEX))

    if resp is None:
        flash('Authorization error with Facebook: reason=%s error=%s' % (request.args['error_reason'],request.args['error_description']))
        return redirect(url_for(INDEX))

    # resp: {'access_token':'token', 'expires':'5181411'}

    set_tokens('facebook', resp['access_token'], '')

    user = facebook.get('/me')
    avatar = facebook.get('/%s/picture?redirect=false' % user.data['id'])

    # user: {'email':'benn@eichhorn.co', 'first_name':'Benn', 'gender':'male', 'id':'10153151264680849', 'last_name':'Eichhorn', 'link':'https://www.facebo...64680849/', 'locale':'en_GB', 'name':'Benn Eichhorn', 'timezone': 11, 'updated_time':'2016-12-02T01:07:31+0000', 'verified': True}
    # avatar: {u'data': {u'is_silhouette': False, u'url': u'https://scontent.x...=58E75933'}}

    set_user(user.data['id'], name=user.data['name'], avatar=avatar.data['data']['url'])

    return redirect(request.args.get('next'))



@auth.route('/twitter')
def twitter_login():
    if not configured(twitter):
        return redirect(url_for(INDEX))
    return twitter.authorize(callback=get_callback('auth.twitter_authorized'))

@auth.route('/twitter/callback')
def twitter_authorized():
    try:
        resp = twitter.authorized_response()
    except OAuthException, e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Twitter: %s' % e.message)
        return redirect(url_for(INDEX))

    if resp is None:
        flash('Authorization error with Twitter: You denied the request to sign in.')
        return redirect(url_for(INDEX))

    # resp: {'oauth_token_secret':'secret', 'user_id':'963683358', 'x_auth_expires':'0', 'oauth_token':'id-token', 'screen_name':'localmeasure'}
    
    # save tokens in session
    set_tokens('twitter', resp['oauth_token'], resp['oauth_token_secret'])

    # get user data
    # https://dev.twitter.com/rest/reference/get/account/verify_credentials#example-response
    user = twitter.get('account/verify_credentials.json')

    # save user in session
    set_user(resp['user_id'], username=['screen_name'], name=user['name'], avatar=user['profile_image_url_https'])

    return redirect(request.args.get('next'))



@auth.route('/instagram')
def instagram_login():
    if not configured(instagram):
        return redirect(url_for(INDEX))
    return instagram.authorize(callback=get_callback('auth.instagram_authorized'))

@auth.route('/instagram/callback')
def instagram_authorized():
    try:
        resp = instagram.authorized_response()
    except OAuthException, e:
        # e.data = 'code': 400,'error_message':'Matching code was ...ady used.','error_type':'OAuthException'}
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Instagram: %s %s' % (e.data['code'],e.data['error_message']))
        return redirect(url_for(INDEX))

    # resp: 'access_token':'token','user':'username':'localmeasure','bio': u'Guest experience and personalization at scale. How well do you know your guests?  \U0001f30e Sydney I Miami I London I Singapore','website':'http://www.localmeasure.com', 'profile_picture':'https://scontent.cdninstagram.com/t....a.jpg','full_name':'Local Measure','id':'262609120'}}

    set_tokens('instagram', resp['access_token'], '')
    set_user(resp['user']['id'], username=resp['user']['username'], name=resp['user']['full_name'], avatar=resp['user']['profile_picture'])

    return redirect(request.args.get('next'))



@auth.route('/weibo')
def weibo_login():
    if not configured(weibo):
        return redirect(url_for(INDEX))
    return weibo.authorize(callback=get_callback('auth.weibo_authorized'))

@auth.route('/weibo/callback')
def weibo_authorized():
    try:
        resp = weibo.authorized_response()
    except OAuthException, e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Weibo: %s' % e.message)
        return redirect(url_for(INDEX))

    if resp is None:
        print 'Access denied for Weibo: request.args=%s' % request.args
        flash('Access denied for Weibo')
        return redirect(url_for(INDEX))

    # resp: EXAMPLE RESPONSE NEEDED

    #TODO: set_tokens('weibo', resp['access_token'], '')
    #TODO: set_user(...)
    flash('Authorization error with Weibo: NOT CONFIGURED')
    return redirect(url_for(INDEX))