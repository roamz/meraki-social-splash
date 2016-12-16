from flask import Flask, redirect, url_for, session, request
from blueprints.common import common
from blueprints.auth import auth, oauth

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

#TODO: load these from environment
app.config['FACEBOOK_CONSUMER_KEY'] = '188477911223606'
app.config['FACEBOOK_CONSUMER_SECRET'] = '621413ddea2bcc5b2e83d42fc40495de'

# lazy loading flask-oauthlib with the Flask config
oauth.init_app(app)

app.register_blueprint(common, url_prefix='')
app.register_blueprint(auth, url_prefix='/auth')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)