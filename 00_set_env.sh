#!/bin/bash 
export DPS_PREFIX="dps"
export DPS_VERSION="v001"
export DPS_SERVICE=""
export AWS_ACCOUNT="058599600888"
export AWS_REGION="eu-central-1"
export AWS_CONTAINER_REGISTRY="dps-container-registry"
export PYTHONPATH="${PYTHONPATH};/home/micha/Documents/dev-aws/aws-data-provider-service/micro-services-python/dps-shared"

echo DPS_PREFIX=$DPS_PREFIX
echo DPS_VERSION=$DPS_VERSION
echo DPS_SERVICE=$DPS_SERVICE
echo AWS_ACCOUNT=$AWS_ACCOUNT
echo AWS_REGION=$AWS_REGION
echo AWS_CONTAINER_REGISTRY=$AWS_CONTAINER_REGISTRY

echo ---------------------------------------------------------