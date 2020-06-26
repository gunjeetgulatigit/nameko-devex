#!/bin/bash

show_help(){
  echo "NEX Deployment needs prefix"
  echo "Usage: "
  # echo "      devops/nex-deploy.sh [-p] [-s] [-x] appname ... where:"
  # echo "      -p means production backing service else dev plan"
  echo "         eg: devops/nex-deploy.sh prefix"
}

while getopts ':px' OPTION; do
  case "$OPTION" in
    p )
			PRODPLAN=TRUE
      ;;
    x )
			SHARED_BACKING=TRUE
      SKIPBROKER=TRUE
      ;;
		\? )
      show_help
			exit 1
      ;;
  esac
done
shift "$(($OPTIND -1))"

# ensure app-prefix is pass in
if [ $# -lt 1 ] ; then
  show_help
  exit 1
fi

PREFIX=$1
echo "Using prefix: $PREFIX"

if [ -z "$PRODPLAN" ]; then
  echo "Using development plan for backing services"
  PLAN_RABBIT=lemur
  PLAN_POSTGRES=turtle
  PLAN_REDIS=30mb
else
  echo "Using production plan for backing services. Not Impl yet"
  PLAN_RABBIT=xxx
  PLAN_POSTGRES=xxx
  PLAN_REDIS=xxxx
fi

# Creating Backing services (may fail if it is already there)
echo "Creating backing service for ${PREFIX}-namekoexample"
cf cs cloudamqp ${PLAN_RABBIT} ${PREFIX}-rabbitmq &
cf cs elephantsql ${PLAN_POSTGRES} ${PREFIX}-postgres &
cf cs rediscloud ${PLAN_REDIS} ${PREFIX}-redis &
wait

# Deploying App(s) in CF
echo "Deploying Application: ${PREFIX} namekoexample"
cp manifest.yml manifest.${PREFIX}.yml


sed -i -e "s/nex/${PREFIX}/g" manifest.${PREFIX}.yml && \
cat manifest.${PREFIX}.yml && \
cf push -f manifest.${PREFIX}.yml

if [ $? -eq 0 ]; then
  rm manifest.${PREFIX}.yml*
fi
