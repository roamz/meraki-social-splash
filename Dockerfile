FROM tiangolo/uwsgi-nginx-flask:flask

# add source code
ADD . /app

COPY ./nginx.conf /etc/nginx/conf.d/

# set up Flask app
RUN pip install -r requirements.txt

# environment vars required by flask app
ENV FACEBOOK_CONSUMER_KEY=NA FACEBOOK_CONSUMER_SECRET=NA TWITTER_CONSUMER_KEY=NA TWITTER_CONSUMER_SECRET=NA INSTAGRAM_CONSUMER_KEY=NA INSTAGRAM_CONSUMER_SECRET=NA WEIBO_CONSUMER_KEY=NA WEIBO_CONSUMER_SECRET=NA

# uwsgi will be running under supervisord recieving requests from nginx
# see here for more info: https://github.com/tiangolo/uwsgi-nginx-flask-docker/
