FROM tiangolo/uwsgi-nginx-flask:flask

# add source code
ADD . /app

COPY ./nginx.conf /etc/nginx/conf.d/

# set up Flask app
RUN pip install -r requirements.txt

# uwsgi will be running under supervisord recieving requests from nginx
# see here for more info: https://github.com/tiangolo/uwsgi-nginx-flask-docker/
