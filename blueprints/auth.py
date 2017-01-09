from flask_oauthlib.client import OAuth, OAuthException
from flask import Blueprint, request, g, url_for, session, redirect, flash
from werkzeug.urls import url_encode, url_decode
import json

INDEX = 'common.index'

auth = Blueprint('auth', __name__)

oauth = OAuth()


def set_state():
    return url_encode({
        'success_url': get_success_url(),
        'failure_url': get_failure_url()
    })

def get_state():
    state = url_decode(request.args.get('state', ''))
    return (
        state.get('success_url', get_success_url()), 
        state.get('failure_url', get_failure_url())
    )


facebook = oauth.remote_app(
    'facebook',
    app_key='FACEBOOK',
    base_url='https://graph.facebook.com',
    request_token_params={
        'state': set_state
    },
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
    request_token_params={
        'state': set_state
    },
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.instagram.com/oauth/access_token',
    authorize_url='https://api.instagram.com/oauth/authorize',
)

weibo = oauth.remote_app(
    'weibo',
    app_key='WEIBO',
    base_url='https://api.weibo.com/2/',
    request_token_params={
        'scope': 'email,statuses_to_me_read',
        'state': set_state
    },
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://api.weibo.com/oauth2/access_token',
    authorize_url='https://api.weibo.com/oauth2/authorize',

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

def set_user(user_id, **kwargs):
    del_user()
    session['user_id']  = user_id

    if kwargs.get('username'):
        session['username'] = kwargs.get('username')

    if kwargs.get('name'):
        session['name'] = kwargs.get('name')

    if kwargs.get('avatar'):
        session['avatar'] = kwargs.get('avatar')

    if kwargs.get('bio'):
        session['bio'] = kwargs.get('bio')

def del_user():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('name', None)
    session.pop('avatar', None)
    session.pop('user_model', None)
    session.pop('bio', None)

def get_success_url():
    return request.args.get('success_url') or request.referrer or url_for(INDEX)

def get_failure_url():
    return request.args.get('failure_url') or request.referrer or url_for(INDEX)

def configured(remote_app):
    if remote_app.consumer_key and remote_app.consumer_secret:
        return True
    print 'ConfigError please configure environment variables for %s_%s and %s_%s' % (remote_app.app_key, remote_app.consumer_key, remote_app.app_key, remote_app.consumer_secret)
    flash('Unable to authorize you with %s because of a bad configuration, please try another method.' % remote_app.app_key.title())
    return False



@auth.route('/facebook')
def facebook_login():
    if not configured(facebook):
        return redirect(get_failure_url())

    callback = url_for('auth.facebook_authorized', _external=True)
    return facebook.authorize(callback=callback)

@auth.route('/facebook/callback')
def facebook_authorized():
    success_url, failure_url = get_state()

    try:
        resp = facebook.authorized_response()
    except OAuthException, e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Facebook: %s' % e.message)
        return redirect(failure_url)

    if resp is None:
        flash('Authorization error with Facebook: reason=%s error=%s' % (request.args['error_reason'],request.args['error_description']))
        return redirect(failure_url)

    # resp: {'access_token':'token', 'expires':'5181411'}

    set_tokens('facebook', resp['access_token'], '')

    user = facebook.get('/me').data
    avatar = facebook.get('/%s/picture?redirect=false&type=large' % user['id']).data

    # user: {'email':'benn@eichhorn.co', 'first_name':'Benn', 'gender':'male', 'id':'10153151264680849', 'last_name':'Eichhorn', 'link':'https://www.facebo...64680849/', 'locale':'en_GB', 'name':'Benn Eichhorn', 'timezone': 11, 'updated_time':'2016-12-02T01:07:31+0000', 'verified': True}
    # avatar: {u'data': {u'is_silhouette': False, u'url': u'https://scontent.x...=58E75933'}}

    set_user(user['id'], username=user['name'], name=user['name'], avatar=avatar['data']['url'])

    return redirect(success_url)



@auth.route('/twitter')
def twitter_login():
    if not configured(twitter):
        return redirect(get_failure_url())

    # Twitter doesnt support state parameter so append states to callback uri
    callback = url_for(
        'auth.twitter_authorized',
        success_url=get_success_url(),
        failure_url=get_failure_url(),
        _external=True
    )
    return twitter.authorize(callback=callback)

@auth.route('/twitter/callback')
def twitter_authorized():
    try:
        resp = twitter.authorized_response()
    except OAuthException, e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Twitter: %s' % e.message)
        return redirect(get_failure_url())

    if resp is None:
        flash('Authorization error with Twitter: You denied the request to sign in.')
        return redirect(get_failure_url())

    # resp: {'oauth_token_secret':'secret', 'user_id':'963683358', 'x_auth_expires':'0', 'oauth_token':'id-token', 'screen_name':'localmeasure'}
    
    # save tokens in session
    set_tokens('twitter', resp['oauth_token'], resp['oauth_token_secret'])

    # get user data
    # https://dev.twitter.com/rest/reference/get/account/verify_credentials#example-response
    user = twitter.get('account/verify_credentials.json').data

    # save user in session
    set_user(resp['user_id'], username=user['screen_name'], name=user['name'], avatar=user['profile_image_url_https'], bio=user['description'])

    return redirect(get_success_url())



@auth.route('/instagram')
def instagram_login():
    if not configured(instagram):
        return redirect(get_failure_url())

    callback = url_for('auth.instagram_authorized', _external=True)
    return instagram.authorize(callback=callback)

@auth.route('/instagram/callback')
def instagram_authorized():
    success_url, failure_url = get_state()

    try:
        resp = instagram.authorized_response()
    except OAuthException, e:
        # e.data = 'code': 400,'error_message':'Matching code was ...ady used.','error_type':'OAuthException'}
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Instagram: %s %s' % (e.data['code'],e.data['error_message']))
        return redirect(failure_url)

    # resp: 'access_token':'token','user':'username':'localmeasure','bio': u'Guest experience and personalization at scale. How well do you know your guests?  \U0001f30e Sydney I Miami I London I Singapore','website':'http://www.localmeasure.com', 'profile_picture':'https://scontent.cdninstagram.com/t....a.jpg','full_name':'Local Measure','id':'262609120'}}

    set_tokens('instagram', resp['access_token'], '')
    user = resp['user']

    set_user(user['id'], username=user['username'], name=user['full_name'], avatar=user['profile_picture'], bio=user['bio'])

    return redirect(success_url)



@auth.route('/weibo')
def weibo_login():
    if not configured(weibo):
        return redirect(get_failure_url())

    callback = url_for('auth.weibo_authorized', _external=True)
    return weibo.authorize(callback=callback)

@auth.route('/weibo/callback')
def weibo_authorized():
    success_url, failure_url = get_state()

    try:
        resp = weibo.authorized_response()
    except OAuthException, e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Weibo: %s' % e.message)
        return redirect(failure_url)

    if resp is None:
        print 'Access denied for Weibo: request.args=%s' % request.args
        flash('Access denied for Weibo')
        return redirect(failure_url)

    print 'Successfull authenticated with Weibo, response looks like this:', resp
    # resp: EXAMPLE RESPONSE NEEDED
    #user = ???
    #set_user(user['id'], username=None, name=None, avatar=None user_model=user)

    #TODO: set_tokens('weibo', resp['access_token'], '')
    #TODO: set_user(...)
    flash('Authorization error with Weibo: NOT FINISHED')
    return redirect(success_url)

