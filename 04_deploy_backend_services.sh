#!/bin/bash 
echo =================================================
echo SETTING ENVIRONMENT
echo =================================================
. ./00_set_env.sh    

echo Deploy DpsBackendServices
echo =================================================
cd ./aws-infra-cdk
cdk deploy DpsBackendServices-$DPS_VERSION
cd ..