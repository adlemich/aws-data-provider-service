from constructs import Construct

from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    Duration,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ssm as ssm
)
from dps_global_definitions.dps_global_definitions import (dps_settings, ServiceDataFargate)

############################################################################
############################################################################
class DpsBackendServices(Stack):

    def __init__(self, scope: Construct, construct_id: str, container_cluster: ecs.Cluster, container_vpc: ec2.Vpc, **kwargs) -> None:
        
        super().__init__(scope, construct_id, **kwargs)

        # Task execution role that allows backend services to interact with AWS Services
        # - SQS
        self.fargate_task_role = iam.Role(
            self,
            dps_settings["application_prefix"] + "-fargate-task-role",
            assumed_by = iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies = [
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSQSFullAccess")
            ],
            role_name = dps_settings["application_prefix"] + "-fargate-task-role"
        )
        # ECS role that allows to pull images from ECR
        self.fargate_ecr_role = iam.Role(
            self,
            dps_settings["application_prefix"] + "-fargate-ecr-access_role",
            assumed_by = iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies = [
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
            ],
            role_name = dps_settings["application_prefix"] + "-fargate-ecr-access_role"
        )

        # Build the central Application Load Balancer
        # Create the load balancer in a VPC. creates an internal load balancer.
        self.container_loadbalancer = elbv2.ApplicationLoadBalancer(
            self, 
            dps_settings["application_prefix"] + "-fargate-cluster-loadbalancer",
            vpc = container_vpc,
            internet_facing = True,
            load_balancer_name = dps_settings["application_prefix"] + "-fargate-cluster-loadbalancer",
        )

        # Add a central listener on port 80
        self.svc_listener = self.container_loadbalancer.add_listener(
            dps_settings["application_prefix"] + "-fargate-cluster-lb-listener-80",
            port = 80,
            default_action = elbv2.ListenerAction.fixed_response(
                status_code = 404,
                message_body = "Bad request, content not found."
            )
        )

        ###############################################################################################################
        ## Build the actual backend services 
        ###############################################################################################################
        self.services_data = [
            ServiceDataFargate(name = "dps-administration-svc",    listen_port = 5001, routing_path = "/" + dps_settings["app_version"] + "/admin"),
            ServiceDataFargate(name = "dps-injest-enpoints-svc",   listen_port = 5002, routing_path = "/" + dps_settings["app_version"] + "/ingest-endpoints"),
            ServiceDataFargate(name = "dps-provider-enpoints-svc", listen_port = 5003, routing_path = "/" + dps_settings["app_version"] + "/provider-endpoints")
        ]

        for i, svc in enumerate(self.services_data):
            self.create_backend_service(
                fargate_ecr_role = self.fargate_ecr_role,
                fargate_task_role = self.fargate_task_role,
                container_cluster = container_cluster,
                container_vpc = container_vpc,
                list_index = i
            )
        
        ###############################################################################################################
        ## Store system wide parameters for the runtime
        ###############################################################################################################
        self.param_version = ssm.StringParameter(
            self, 
            dps_settings["application_prefix"] + "-version" + "-param",
            description = "Version of Data Provider Service.",
            parameter_name = "/" + dps_settings["application_prefix"] + "/system/version",
            string_value = dps_settings["app_version"]
        )

        self.param_lb_url = ssm.StringParameter(
            self, 
            dps_settings["application_prefix"] + "-fargate-app-lb-dns" + "-param",
            description = "Public DNS URL for web API of the Data Provider Service.",
            parameter_name = "/" + dps_settings["application_prefix"] + "/system/public-api-url",
            string_value = "http://" + self.container_loadbalancer.load_balancer_dns_name + "/" + dps_settings["app_version"] + "/"
        )

        self.param_log_level = ssm.StringParameter(
            self, 
            dps_settings["application_prefix"] + "-sys-logging-level" + "-param",
            description = "Global logging level Data Provider Service.",
            parameter_name = "/" + dps_settings["application_prefix"] + "/system/logging/log-level",
            string_value = "INFO"
        )

        ###############################################################################################################
        ### OUTPUT
        ###############################################################################################################
        CfnOutput(self, 
            dps_settings["application_prefix"] + "-fargate-app-loadbalancer" + "-cfn-out", 
            value = self.container_loadbalancer.load_balancer_arn)
        
        CfnOutput(self, 
            dps_settings["application_prefix"] + "-fargate-app-lb-dns" + "-cfn-out", 
            value = self.container_loadbalancer.load_balancer_dns_name)
    
    
    ###############################################################################################################
    ###############################################################################################################
    ###############################################################################################################
    def create_backend_service(self, fargate_ecr_role: iam.Role, fargate_task_role: iam.Role, container_cluster: ecs.Cluster, container_vpc: ec2.Vpc, list_index: int) -> None:

        # Create a target group for the ALB for each backend service
        self.services_data[list_index].container_alb_target_grp = elbv2.ApplicationTargetGroup(
            self,
            self.services_data[list_index].name + "-tgt-grp",
            port = 80,
            protocol = elbv2.ApplicationProtocol.HTTP,
            deregistration_delay = Duration.minutes(1),
            target_group_name = self.services_data[list_index].name + "-tgrp",
            target_type = elbv2.TargetType.IP,
            vpc = container_vpc
        )

        #Add action to ALB with the right route to map to the target group
        self.svc_listener.add_action(
            self.services_data[list_index].name + "-listner-rule",
            action = elbv2.ListenerAction.forward(target_groups = [self.services_data[list_index].container_alb_target_grp]),
            conditions = [
                #elbv2.ListenerCondition.host_headers(["example.com"]),
                elbv2.ListenerCondition.path_patterns([self.services_data[list_index].routing_path])
            ],
            priority = self.services_data[list_index].listen_port
        )

        # A log group for this backend service
        self.services_data[list_index].log_group = logs.LogGroup(
            self, 
            self.services_data[list_index].name + "-loggroup", 
            log_group_name = self.services_data[list_index].name + "-loggroup", 
            removal_policy = RemovalPolicy.DESTROY,
            retention = logs.RetentionDays.ONE_MONTH
        )

        # Define Task Definition for each backend service
        self.services_data[list_index].fargate_taskdef = ecs.FargateTaskDefinition(
            self, 
            self.services_data[list_index].name + "-taskdef",
            execution_role = fargate_ecr_role,
            task_role = fargate_task_role
        )

        # Define which docker container to use and its details
        self.services_data[list_index].fargate_taskdef.add_container(
            self.services_data[list_index].name + "-container",
            container_name = self.services_data[list_index].name + "-container",
            image = ecs.ContainerImage.from_registry(dps_settings["aws_account_nr"] + ".dkr.ecr." + dps_settings["aws_region"] + ".amazonaws.com/" 
                + dps_settings["aws_container_registry"] + ":" + self.services_data[list_index].name + "-" + dps_settings["app_version"]),
            environment = { 
                # clear text, not for sensitive data
                "STAGE": "prototype",
                "DPS_PREFIX": dps_settings["application_prefix"],
                "DPS_VERSION": dps_settings["app_version"]
            },
            logging = ecs.LogDrivers.aws_logs(
                stream_prefix = self.services_data[list_index].name,
                log_group = self.services_data[list_index].log_group
            ),
            port_mappings = [
                ecs.PortMapping(container_port = self.services_data[list_index].listen_port, 
                protocol = ecs.Protocol.TCP)] 
        )

        # Fargate Service for this backend 
        self.services_data[list_index].fargate_service = ecs.FargateService(self,
            self.services_data[list_index].name + "-service",
            assign_public_ip = False,
            cluster = container_cluster,
            vpc_subnets = ec2.SubnetSelection(subnet_type = ec2.SubnetType.PRIVATE_ISOLATED),
            desired_count = dps_settings["aws_ecs_cluster_ec2_size"],
            max_healthy_percent = 200,
            min_healthy_percent = 50,
            service_name = self.services_data[list_index].name + "-service",
            task_definition = self.services_data[list_index].fargate_taskdef
        )
        
        # Set scaling parameters for this service
        self.services_data[list_index].fargate_svc_scaling = self.services_data[list_index].fargate_service.auto_scale_task_count(
            min_capacity = 1,
            max_capacity = dps_settings["aws_ecs_cluster_ec2_size"] * 2)
        self.services_data[list_index].fargate_svc_scaling.scale_on_cpu_utilization(
            self.services_data[list_index].name + "-fargate-cluster-cpuscaling",
            target_utilization_percent = 75)
        self.services_data[list_index].fargate_svc_scaling.scale_on_memory_utilization(
            self.services_data[list_index].name + "-memoryscaling",
            target_utilization_percent = 75)

        # Add service to load balancer targets
        self.services_data[list_index].container_alb_target_grp.add_target(self.services_data[list_index].fargate_service)
        
        ### OUTPUT
        #################################################################
        CfnOutput(self, 
            self.services_data[list_index].name + "-service" + "-cfn-out",
            value = self.services_data[list_index].fargate_service.service_arn)
