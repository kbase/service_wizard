#!/bin/sh


if [ ! -z "$CONF_URL" ] ; then
   ENV="-env $CONF_URL"
fi

if [ ! -z "$SECRET" ] ; then
  ENVHEADER="--env-header /run/secrets/$SECRET"
fi

dockerize \
  $ENV \
  $ENVHEADER \
  -validate-cert=false \
  -template /kb/deployment/conf/.templates/deployment.cfg.templ:/kb/deployment/conf/deployment.cfg

exec uwsgi --master --processes 5 --threads 5 --http :5000 --wsgi-file ./lib/biokbase/ServiceWizard/Server.py
