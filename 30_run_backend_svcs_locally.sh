#!/bin/bash 
clear
echo =================================================
echo SETTING ENVIRONMENT
echo =================================================
. ./00_set_env.sh  

cd ./micro-services-python

PORT_NO=5000

for dir in ./*/     
do
    dir=${dir%*/}      # remove the trailing "/"
    DPS_SERVICE=${dir##*/}
    echo BUILDING DOCKER IMAGE FOR BACKEND SERVICE $DPS_SERVICE
    cd ./$DPS_SERVICE
    docker build --tag $AWS_CONTAINER_REGISTRY:$DPS_SERVICE-$DPS_VERSION .

    echo RUN LOCAL IMAGE FOR $DPS_SERVICE
    PORT_NO=$((PORT_NO+1))
    docker run -d -p $PORT_NO:$PORT_NO $AWS_CONTAINER_REGISTRY:$DPS_SERVICE-$DPS_VERSION

    cd ..
    echo =================================================
done

echo Check currently running images...
docker ps

cd ..