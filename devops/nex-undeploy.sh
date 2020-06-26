#!/bin/bash

show_help(){
  echo "NEX Deployment needs prefix"
  echo "Usage: "
  echo "      devops/nex-undeploy.sh appname ... where:"
  # echo "      -p means production backing service else dev plan"
  echo "         eg: devops/pmc-undeploy.sh appname"
}

# ensure app-prefix is pass in
if [ $# -lt 1 ] ; then
  show_help
  exit 1
fi

PREFIX=$1
echo "Using prefix: $PREFIX"

DOMAIN=$(cf domains | grep 'shared' | head -n 1 | awk '{print $1}')


# 3. Delete Apps and Services
cf services > services.log
SERVICES=($(cat services.log | awk '/name/{p=1}{if (p) print}' | awk '{print $1}' | grep -v name | grep $PREFIX))
APPS=($(cf apps | awk '/name/{p=1}{if (p) print}' | awk '{print $1}' | grep -v '^name$' | grep $PREFIX))

echo "Apps    : ${APPS[@]}"
echo "Services: ${SERVICES[@]}"

for service in "${SERVICES[@]}"; do
  BOUND_APPS=($(cf service ${service} | grep ^${PREFIX} | awk '{print $1}'))
  for bound_app in "${BOUND_APPS[@]}"; do
    cf unbind-service ${bound_app} ${service} &
  done
  wait
  cf delete-service -f $service &
done
rm services.log
wait

for app in "${APPS[@]}"; do
    if [[ $app != *"-broker" ]]; then
      echo "deleting app: $app"
      cf delete-route ${DOMAIN} --hostname $app -f
      cf delete -f $app
    fi
done
