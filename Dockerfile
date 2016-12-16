FROM tiangolo/uwsgi-nginx-flask:flask

# set up Ubuntu
#RUN apt-get update -y
#RUN apt-get install -y apt-utils tar curl wget build-essential git
#RUN apt-get install -y python python-dev python-distribute python-pip build-essential git

# add source code
ADD . /app
#WORKDIR /app

# set up Flask app
#RUN pip install -r requirements.txt
