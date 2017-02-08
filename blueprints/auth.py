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

USER_FIELDS = [
    'username',
    'name',
    'avatar',
    'bio'
]

def set_user(user_id, **kwargs):
    del_user()
    session['user_id'] = user_id
    for field in USER_FIELDS:
        if kwargs.get(field):
            session[field] = kwargs.get(field)

def del_user():
    session.pop('user_id', None)
    for field in USER_FIELDS:
        session.pop(field, None)

def get_success_url():
    return request.args.get('success_url') or request.referrer or url_for(INDEX)

def get_failure_url():
    return request.args.get('failure_url') or request.referrer or url_for(INDEX)

def configured(remote_app):
    if remote_app.consumer_key and remote_app.consumer_secret:
        return True

    flash('Unable to authorize you with %s because of a bad configuration, please try another method.' % remote_app.app_key.title())
    return False

@auth.route('/facebook')
def facebook_login():
    if not configured(facebook):
        return redirect(get_failure_url())

    callback = url_for('auth.facebook_authorized',
        success_url=get_success_url(),
        failure_url=get_failure_url(),
        _external=True
    )
    return facebook.authorize(callback=callback)

@auth.route('/facebook/callback')
def facebook_authorized():
    success_url, failure_url = get_state()

    resp = None
    try:
        resp = facebook.authorized_response()
    except OAuthException, e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Facebook: %s' % e.message)
        return redirect(failure_url)
    except Exception as e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Facebook: %s' % e.message)
        return redirect(failure_url)

    if resp is None:
        flash('Authorization error with Facebook: reason=%s error=%s' % (request.args['error_reason'],request.args['error_description']))
        return redirect(failure_url)

    # resp: {'access_token':'token', 'expires':'5181411'}
    try:
        set_tokens('facebook', resp['access_token'], '')
    except Exception as e:
        print 'Unable to set access_token for Facebook {}'.format(e)
        flash('Unable to set access_token for Facebook')
        return redirect(failure_url)

    user = {}
    try:
        user = facebook.get('/me?fields=about,email,id,name').data
        avatar = facebook.get('/%s/picture?redirect=false&type=large' % user['id']).data

        kwargs = {}
        kwargs['username'] = user.get('name')
        kwargs['name'] = user.get('name')
        kwargs['avatar'] = avatar.get('data', {}).get('url')
        set_user(user['id'], **kwargs)
    except Exception as e:
        print 'exception getting and setting facebook user {}'.format(e)
        pass

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
    success_url, failure_url = get_state()
    try:
        resp = twitter.authorized_response()
    except OAuthException, e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Twitter: %s' % e.message)
        return redirect(failure_url)

    if resp is None:
        flash('Authorization error with Twitter: reason=%s error=%s' % (request.args['error_reason'],request.args['error_description']))
        return redirect(failure_url)

    # save tokens in session
    try:
        set_tokens('twitter', resp['oauth_token'], resp['oauth_token_secret'])
    except Exception as e:
        print 'Unable to set access_token for Instagram {}'.format(e)
        flash('Unable to set oauth_token for Twitter')
        return redirect(failure_url)

    # get user data
    try:
        user = twitter.get('account/verify_credentials.json').data
        # save user in session
        kwargs = {}
        kwargs['username'] = user.get('screen_name')
        kwargs['name'] = user.get('name')
        kwargs['avatar'] = user.get('profile_image_url_https')
        kwargs['bio'] = user.get('description')
        set_user(resp['user_id'], **kwargs)
    except Exception as e:
        print 'exception getting and setting Twitter user {}'.format(e)
        pass

    return redirect(success_url)



@auth.route('/instagram')
def instagram_login():
    if not configured(instagram):
        return redirect(get_failure_url())

    callback = url_for('auth.instagram_authorized',
        success_url=get_success_url(),
        failure_url=get_failure_url(),
        _external=True
    )
    return instagram.authorize(callback=callback)

@auth.route('/instagram/callback')
def instagram_authorized():
    success_url, failure_url = get_state()

    try:
        resp = instagram.authorized_response()
    except OAuthException, e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Instagram: %s %s' % (e.data['code'], e.data['error_message']))
        return redirect(failure_url)
    except Exception as e:
        flash('Unable to set access_token for Weibo')
        return redirect(failure_url)

    if resp is None:
        flash('Authorization error with Instagram: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description']))
        return redirect(failure_url)

    try:
        set_tokens('instagram', resp['access_token'], '')
    except Exception as e:
        print 'Unable to set access_token for Instagram {}'.format(e)
        flash('Unable to set access_token for Instagram')
        return redirect(failure_url)

    try:
        user = resp['user']
        kwargs = {}
        kwargs['username'] = user.get('username')
        kwargs['name'] = user.get('full_name')
        kwargs['avatar'] = user.get('profile_picture')
        kwargs['bio'] = user.get('bio')
        set_user(user['id'], **kwargs)
    except Exception as e:
        print 'exception getting and setting instagram user {}'.format(e)
        pass

    return redirect(success_url)



@auth.route('/weibo')
def weibo_login():
    if not configured(weibo):
        return redirect(get_failure_url())

    callback = url_for('auth.weibo_authorized', _external=True)
    callback = callback.replace('http://localhost:4000', 'https://wifi.getlocalmeasure.com')
    return weibo.authorize(callback=callback)

@auth.route('/weibo/callback')
def weibo_authorized():
    success_url, failure_url = get_state()

    resp = None
    try:
        resp = weibo.authorized_response()
    except OAuthException, e:
        print 'OAuthException', e.message, e.data
        flash('Authorization error with Weibo: %s' % e.message)
        return redirect(failure_url)
    except Exception as e:
        flash('Unable to set access_token for Weibo')
        return redirect(failure_url)

    if resp is None:
        print 'Access denied for Weibo: request.args=%s' % request.args
        flash('Authorization error with Weibo: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description']))
        return redirect(failure_url)

    print 'resp = {}'.format(resp)
    try:
        set_tokens('weibo', resp['access_token'], '')
    except Exception as e:
        print 'Unable to set access_token for Weibo'
        flash('Unable to set access_token for Weibo')
        return redirect(failure_url)

    try:
        user = weibo.get('users/show.json?uid={}&access_token={}'.format(resp['uid'], resp['access_token'])).data
        kwargs = {}
        kwargs['username'] = user.get('screen_name')
        kwargs['name'] = user.get('name')
        kwargs['avatar'] = user.get('avatar_large')
        kwargs['bio'] = user.get('description')
        set_user(user['id'], **kwargs)
    except Exception as e:
        print 'exception getting and setting weibo user {}'.format(e)
        pass

    return redirect(success_url)

