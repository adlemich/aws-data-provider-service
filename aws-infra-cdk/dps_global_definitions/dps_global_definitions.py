import os
from dataclasses import dataclass
from aws_cdk import (
    aws_ecs as ecs,
    aws_logs as logs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam
)

############################################################################
# Defines global variables around the AWS setup
############################################################################
dps_settings = {
    "application_prefix": os.getenv('DPS_PREFIX'),
    "app_version": os.getenv('DPS_VERSION'),
    "aws_account_nr": os.getenv('AWS_ACCOUNT'),
    "aws_region": os.getenv('AWS_REGION'),
    
    "aws_container_registry": os.getenv('AWS_CONTAINER_REGISTRY'),
    "data_retention_days": 30,
    
    "aws_ecs_cluster_ec2_type": "t2.xlarge",
    "aws_ecs_cluster_ec2_size": 2,

    "aws_backend_loadbalancer_url": os.getenv('AWS_BACKEND_LB_URL') # to be stored by backend service stack
}

@dataclass
class ServiceDataFargate:
    name: str
    listen_port: int
    routing_path: str
    log_group:  logs.LogGroup = None
    fargate_taskdef: ecs.FargateTaskDefinition = None
    fargate_service: ecs.FargateService = None
    fargate_svc_scaling: ecs.ScalableTaskCount = None
    container_alb_target_grp: elbv2.ApplicationTargetGroup = None
    service_iam_user: iam.User = None
    access_key: iam.AccessKey = None
    

