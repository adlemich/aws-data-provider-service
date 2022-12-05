#!/bin/bash 
echo =================================================
echo SETTING ENVIRONMENT
echo =================================================
. ./00_set_env.sh  

echo LOGIN DOCKER TO AWS ECR
echo =================================================
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com

cd ./micro-services-python

for dir in ./dps*/
do
    dir=${dir%*/}      # remove the trailing "/"
    DPS_SERVICE=${dir##*/}
    echo $DPS_SERVICE

    echo BUILDING BACKEND SERVICE $DPS_SERVICE
    cd ./$DPS_SERVICE
    docker build --tag $AWS_CONTAINER_REGISTRY:$DPS_SERVICE-$DPS_VERSION .

    echo UPLOADING DOCKER IMAGE FOR $DPS_SERVICE TO ECR
    docker tag $AWS_CONTAINER_REGISTRY:$DPS_SERVICE-$DPS_VERSION $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_CONTAINER_REGISTRY:$DPS_SERVICE-$DPS_VERSION 
    docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_CONTAINER_REGISTRY:$DPS_SERVICE-$DPS_VERSION
    cd ..
    echo =================================================

done
cd ..