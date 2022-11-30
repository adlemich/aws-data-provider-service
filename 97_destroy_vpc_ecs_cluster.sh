#!/bin/bash 
echo =================================================
echo SETTING ENVIRONMENT
echo =================================================
. ./00_set_env.sh  

echo Destroy DpsVPCFargateCluster
echo =================================================
cd ./aws-infra-cdk
cdk destroy -f DpsVPCFargateCluster-$DPS_VERSION
cd ..