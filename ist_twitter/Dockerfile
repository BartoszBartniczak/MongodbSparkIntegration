FROM ubuntu:14.04

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update \
    && apt-get install -y python-pip python-dev
RUN apt-get install -y libyaml-cpp0.3-dev libffi-dev libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

RUN pip install tweepy pymongo pyaml pyopenssl ndg-httpsclient pyasn1
VOLUME ["/code"]
WORKDIR ["/code"]

CMD ["python","/code/importTweets.py"]

