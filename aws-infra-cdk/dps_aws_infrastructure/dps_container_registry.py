from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_ecr as ecr,
)
from dps_global_definitions.dps_global_definitions import dps_settings
from constructs import Construct

############################################################################
############################################################################
##
## AWS Ressources stack for private Container Registry:
##  - ECR: Private Repository with max container image age of 30 days.
##
############################################################################
class DpsContainerRegistry(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECR CONTAINER REGISTRY FOR DOCKER IMAGES        
        docker_repo_name = dps_settings["aws_container_registry"]
        self.docker_repo = ecr.Repository(self, 
            docker_repo_name,
            repository_name = docker_repo_name,
            image_scan_on_push = True,
            removal_policy = RemovalPolicy.DESTROY)

        self.docker_repo.add_lifecycle_rule(max_image_age = Duration.days(dps_settings["data_retention_days"]))

        ### OUTPUT
        #################################################################
        CfnOutput(self, 
            dps_settings["aws_container_registry"] + "-cfn-out",
            value = self.docker_repo.repository_arn)