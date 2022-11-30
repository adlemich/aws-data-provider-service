#!/bin/bash 
echo =================================================
echo SETTING ENVIRONMENT
echo =================================================
. ./00_set_env.sh  

echo Destroy DpsContainerRegistry
echo =================================================
cd ./aws-infra-cdk
cdk destroy -f DpsContainerRegistry-$DPS_VERSION
cd ..