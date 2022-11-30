#!/bin/bash 
echo =================================================
echo SETTING ENVIRONMENT
echo =================================================
. ./00_set_env.sh    

echo Deploy DpsVPCFargateCluster
echo =================================================
cd ./aws-infra-cdk
cdk deploy DpsVPCFargateCluster-$DPS_VERSION
cd ..