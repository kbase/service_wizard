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

exec uwsgi --master \
  --processes ${PROCESSES:-5} \
  --threads ${THREADS:-5} \
  --http :${PORT:-5000} \
  --http-timeout ${TIMEOUT:-600} \
  --wsgi-file ./lib/biokbase/ServiceWizard/Server.py
