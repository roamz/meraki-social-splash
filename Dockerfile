FROM tiangolo/uwsgi-nginx-flask:flask

# add source code
ADD . /app

# set up Flask app
RUN pip install -r requirements.txt
