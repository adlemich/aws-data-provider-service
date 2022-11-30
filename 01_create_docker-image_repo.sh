#!/bin/bash 
echo =================================================
echo SETTING ENVIRONMENT
echo =================================================
. ./00_set_env.sh    

echo Deploy DpsContainerRegistry
echo =================================================
cd ./aws-infra-cdk
cdk deploy DpsContainerRegistry-$DPS_VERSION
cd ..
