#!/bin/bash 
echo =================================================
echo SETTING ENVIRONMENT
echo =================================================
. ./00_set_env.sh  

echo LOGIN DOCKER TO AWS ECR
echo =================================================
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com

cd ./micro-services-python

for dir in ./*/     
do
    dir=${dir%*/}      # remove the trailing "/"
    DPS_SERVICE=${dir##*/}
    echo REMOVING IMAGES FOR BACKEND SERVICE $DPS_SERVICE
    aws ecr batch-delete-image --repository-name $AWS_CONTAINER_REGISTRY --region $AWS_REGION --image-ids imageTag=$DPS_SERVICE-$DPS_VERSION
    docker image rm --force $AWS_CONTAINER_REGISTRY:$DPS_SERVICE-$DPS_VERSION 
    docker image rm --force $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_CONTAINER_REGISTRY:$DPS_SERVICE-$DPS_VERSION
    cd ..
    echo =================================================
done

docker container prune --force
docker image prune -a --force
cd ..
