FROM python:3.9-slim-buster

# These ARGs values are passed in via the docker build command
ARG BUILD_DATE
ARG VCS_REF
ARG BRANCH=develop

ENV KB_DEPLOYMENT_CONFIG /kb/deployment/conf/deployment.cfg

SHELL ["/bin/bash", "-c"]

RUN apt-get -y update && apt-get -y install wget

# Install dockerize
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/kbase/dockerize/raw/master/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz && \
    tar -C /usr/bin -xvzf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz && \
    rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz


#TODO Remove this?
ADD ./deps/rancher-compose.sh /tmp/
RUN sh /tmp/rancher-compose.sh

RUN apt-get -y upgrade && apt-get install -y gcc git vim


ADD requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ADD . /kb/deployment/

RUN mv /kb/deployment/deployment/conf/.templates /kb/deployment/conf/

# The BUILD_DATE value seem to bust the docker cache when the timestamp changes, move to
# the end
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/kbase/service_wizard.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0-rc1" \
      us.kbase.vcs-branch=$BRANCH \
      maintainer="Steve Chan sychan@lbl.gov"

ENV PYTHONPATH=/kb/deployment/lib
WORKDIR /kb/deployment/
ENTRYPOINT [ "/kb/deployment/entrypoint.sh"]