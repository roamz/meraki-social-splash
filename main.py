import os
from flask import Flask, redirect, url_for, session, request
from blueprints.common import common
from blueprints.auth import auth, oauth

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

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

app.register_blueprint(common, url_prefix='')
app.register_blueprint(auth, url_prefix='/auth')

if __name__ == '__main__':
    app.run()