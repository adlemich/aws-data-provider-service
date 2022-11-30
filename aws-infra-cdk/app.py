#!/usr/bin/env python3
import aws_cdk as cdk

from dps_global_definitions.dps_global_definitions import dps_settings
from dps_aws_infrastructure.dps_container_registry import DpsContainerRegistry 
from dps_aws_infrastructure.dps_vpc_fargate_cluster import DpsVPCFargateCluster
from dps_aws_infrastructure.dps_backend_services import DpsBackendServices

app = cdk.App()
############################################################################
cont_Reg = DpsContainerRegistry(
    app, 
    "DpsContainerRegistry-" + dps_settings["app_version"],
    env = cdk.Environment(account = dps_settings["aws_account_nr"], 
    region = dps_settings["aws_region"])    
)

############################################################################
vpc_fargate = DpsVPCFargateCluster(
    app, 
    "DpsVPCFargateCluster-" + dps_settings["app_version"],
    env = cdk.Environment(account = dps_settings["aws_account_nr"], 
    region = dps_settings["aws_region"])    
)

############################################################################
back_svcs = DpsBackendServices(
    app, 
    "DpsBackendServices-" + dps_settings["app_version"],
    container_cluster = vpc_fargate.container_cluster,
    container_vpc = vpc_fargate.container_vpc,
    env = cdk.Environment(account = dps_settings["aws_account_nr"], 
    region = dps_settings["aws_region"])    
)
    
app.synth()