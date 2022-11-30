from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_ecs as ecs
)
from dps_global_definitions.dps_global_definitions import dps_settings

############################################################################
############################################################################
class DpsVPCFargateCluster(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC with private and public subnets to run the ECS cluster
        self.container_vpc = ec2.Vpc(
            self, 
            dps_settings["application_prefix"] + "-fargate-cluster-vpc",
            max_azs = 2,
            subnet_configuration = [
                ec2.SubnetConfiguration(
                    name = dps_settings["application_prefix"] + "-fargate-cluster-vpc-subnet-priv",
                    subnet_type = ec2.SubnetType.PRIVATE_ISOLATED,
                    reserved = False,
                ),
                ec2.SubnetConfiguration(
                    name = dps_settings["application_prefix"] + "-fargate-cluster-vpc-subnet-pub",
                    subnet_type = ec2.SubnetType.PUBLIC,
                    reserved = False
                )
            ]
        )

        # Adding VPC interface endpoints for all required services to keep the containers in private networks
        self.container_vpc.add_interface_endpoint(dps_settings["application_prefix"] + "-fargate-cluster-vpc-ep-ecr",
            service = ec2.InterfaceVpcEndpointAwsService.ECR)
        self.container_vpc.add_interface_endpoint(dps_settings["application_prefix"] + "-fargate-cluster-vpc-ep-docker",
            service = ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER)
        self.container_vpc.add_interface_endpoint(dps_settings["application_prefix"] + "-fargate-cluster-vpc-ep-logs",
            service = ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS)
        self.container_vpc.add_interface_endpoint(dps_settings["application_prefix"] + "-fargate-cluster-vpc-ep-watch",
            service = ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH)
        self.container_vpc.add_interface_endpoint(dps_settings["application_prefix"] + "-fargate-cluster-vpc-ep-events",
            service = ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_EVENTS)
        self.container_vpc.add_gateway_endpoint(dps_settings["application_prefix"] + "-fargate-cluster-vpc-ep-s3",
            service = ec2.GatewayVpcEndpointAwsService.S3)

        # Creating the actual ECS Cluster and Fargate service, autoscaling
        self.container_cluster = ecs.Cluster(
            self, 
            dps_settings["application_prefix"] + '-fargate-cluster-autoscaling',
            vpc = self.container_vpc,
            cluster_name = dps_settings["application_prefix"] + '-fargate-cluster-autoscaling',
            enable_fargate_capacity_providers = True, 
        )

        # Setting inital size of the cluster
        self.container_cluster.add_capacity(dps_settings["application_prefix"] + "dps-fargate-autoscalinggroup-capacity",
            instance_type = ec2.InstanceType(dps_settings["aws_ecs_cluster_ec2_type"]),
            desired_capacity = dps_settings["aws_ecs_cluster_ec2_size"]
        )

        ## OUTPUT
        #############################################################################
        CfnOutput(self, 
            dps_settings["application_prefix"] + '-fargate-cluster-autoscaling' + "-cfn-out", 
            value = self.container_cluster.cluster_arn)