#!/bin/bash 
echo =================================================
echo SETTING ENVIRONMENT
echo =================================================
. ./00_set_env.sh  

echo Destroy DpsBackendServices
echo =================================================
cd ./aws-infra-cdk
cdk destroy -f DpsBackendServices-$DPS_VERSION
cd ..