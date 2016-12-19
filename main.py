import os
from flask import Flask, redirect, url_for, session, request
from blueprints.common import common
from blueprints.auth import auth, oauth

app = Flask(__name__)
app.debug = True
app.secret_key = '\xc2\x175R=\x9e\xed\xfaz\x89\x0c\xb1mQ;\xf2\x1e\xf7\x9bx\xee\xc0\x85\xb6'

# TODO: SESSION STORAGE BACKED BY REDIS
# Support multiple docker containers with central redis backed session storage
# http://flask.pocoo.org/snippets/75/


# load required oauth config from environment
app.config['FACEBOOK_CONSUMER_KEY'] = os.environ.get('FACEBOOK_CONSUMER_KEY')
app.config['FACEBOOK_CONSUMER_SECRET'] = os.environ.get('FACEBOOK_CONSUMER_SECRET')
app.config['TWITTER_CONSUMER_KEY'] = os.environ.get('TWITTER_CONSUMER_KEY')
app.config['TWITTER_CONSUMER_SECRET'] = os.environ.get('TWITTER_CONSUMER_SECRET')
app.config['INSTAGRAM_CONSUMER_KEY'] = os.environ.get('INSTAGRAM_CONSUMER_KEY')
app.config['INSTAGRAM_CONSUMER_SECRET'] = os.environ.get('INSTAGRAM_CONSUMER_SECRET')
app.config['WEIBO_CONSUMER_KEY'] = os.environ.get('WEIBO_CONSUMER_KEY')
app.config['WEIBO_CONSUMER_SECRET'] = os.environ.get('WEIBO_CONSUMER_SECRET')

# lazy loading flask-oauthlib with the Flask config
oauth.init_app(app)

# load routes
app.register_blueprint(common, url_prefix='')
app.register_blueprint(auth, url_prefix='/auth')


if __name__ == '__main__':
    app.run()