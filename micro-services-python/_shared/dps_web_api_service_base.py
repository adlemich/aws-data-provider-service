from flask import (
    Flask, 
    request, 
    jsonify, 
    Response
)
import logging
from http import HTTPStatus
import boto3
from botocore.config import Config
import botocore.exceptions
import botocore.errorfactory
import os
import uuid

#####################################################################################
class DpsWebApiServiceBase:
    # Global constants
    app_prefix: str
    service_version: str
    instance_id: str

    # Dynamic data
    flask_app: Flask
    service_name: str    
    service_route_prefix: str
    service_log_prefix: str    

    # application parameters
    sys_param_log_level: str

    # aws client instances
    aws_region = None
    aws_config = None
    aws_ssm_client = None
    aws_key = None
    aws_secret = None

    #####################################################################################
    def __init__(self, flask_app: Flask, service_name: str, service_route: str) -> None:

        self.flask_app = flask_app
        self.service_name = service_name
        self.instance_id = service_name + "-" + str(uuid.uuid4())

        # Read and check anvrionment 
        self.read_check_env()

        ## APPLICATION PARAMTERS SYSTEM LEVEL
        self.sys_param_log_level = "/{}/system/logging/log-level".format(self.app_prefix)

        ## SET SOME LOGGING SETTINGS        
        logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s')
        self.flask_app.logger.setLevel("INFO")
        self.service_log_prefix = "{}: ".format(service_name)

        # Set up AWS 
        self.setup_aws()

        # Routing for service APIs
        self.service_route_prefix = "/{}{}".format(self.service_version, service_route)

        self.flask_app.logger.info("STARTING UP. app_prefix = [{}], service_version = [{}], service_route = [{}], instance_id = [{}]".format( 
            self.app_prefix, self.service_version, service_route, self.instance_id))
        return

    #####################################################################################
    def read_check_env(self) -> None:

        self.app_prefix = os.getenv('DPS_PREFIX')
        self.service_version = os.getenv('DPS_VERSION')
        self.aws_region = os.getenv('AWS_REGION')
        self.aws_key = os.getenv('AWS_KEY')
        self.aws_secret = os.getenv('AWS_SECRET')

        if (self.app_prefix == None) or (len(self.app_prefix) < 1):
            self.flask_app.logger.error("Failed to load App Prefix from environment. Is env variable DPS_PREFIX set correctly?")

        if (self.service_version == None) or (len(self.service_version) < 1):
            self.flask_app.logger.error("Failed to load Service Version from environment. Is env variable DPS_VERSION set correctly?")

        if (self.aws_region == None) or (len(self.aws_region) < 1):
            self.flask_app.logger.error("Failed to load AWS region from environment. Is env variable AWS_REGION set correctly?")

        if (self.aws_key == None) or (len(self.aws_key) < 1):
            self.flask_app.logger.error("Failed to load AWS key from environment. Is env variable AWS_KEY set correctly?")

        if (self.aws_secret == None) or (len(self.aws_secret) < 1):
            self.flask_app.logger.error("Failed to load AWS secret from environment. Is env variable AWS_SECRET set correctly?")

        return 

    #####################################################################################
    def setup_aws(self) -> None:

        ## AWS Base configuration
        self.aws_config = Config(
            region_name = self.aws_region,
            signature_version = 'v4',
            retries = {
                'max_attempts': 10,
                'mode': 'standard'
            },
            connect_timeout = 60,
            max_pool_connections = 2
        )

        # AWS Client for Systems Manager (used to get Application Parameters)
        try:
            self.aws_ssm_client = boto3.client('ssm', 
                config = self.aws_config,
                aws_access_key_id = self.aws_key,
                aws_secret_access_key = self.aws_secret
            )
        except botocore.exceptions.NoRegionError:
            self.flask_app.logger.error("Can not setup AWS client for SSM, no AWS region specified. Is env variable AWS_REGION set correctly?")
        except:
            self.flask_app.logger.error("Unknown error while creating AWS SSM Client!")
        
        return

    #####################################################################################
    def get_service_name(self) -> str:
        return self.service_name

    #####################################################################################
    def get_service_version(self) -> str:
        return self.service_version
    
    #####################################################################################
    def get_service_route_prefix(self) -> str:
        return self.service_route_prefix

    #####################################################################################
    def handle_health_check(self) -> Response:
        self.flask_app.logger.debug("Handling health check...")

        # read global parameters and update local data
        param_log_level = self.read_app_parameter(self.sys_param_log_level)
        if param_log_level != None:
            self.flask_app.logger.setLevel(param_log_level)
            self.flask_app.logger.debug("Applied log-level parameter set to [{}]".format(param_log_level))

        # Provide status response
        response_set = jsonify(
            result = HTTPStatus.OK, 
            message = "Health Check OK!", 
            hints = "Service [" + self.service_name + "]"
        )
        response_set.status = HTTPStatus.OK 
        
        return response_set

    #####################################################################################
    def write_app_parameter(self, param_name: str, new_value: str) -> None:
        self.flask_app.logger.debug("Now updating application parameter [{}] in AWS SSM with value: [{}]".format(
            param_name, new_value))

        try:
            self.aws_ssm_client.put_parameter(
                Name = param_name,
                Value = new_value,
                Overwrite = True,
                Type = "String",
                Tier = "Standard"
            )
        except botocore.exceptions.NoCredentialsError:
            self.flask_app.logger.error(
                "Could not write application parameter [{}] to AWS SSM. No credentials found. Did you configure the AWS credentials Key and SecretKey?".format(param_name))
            return None
        except botocore.exceptions.EndpointConnectionError:
            self.flask_app.logger.error(
                "Could not write application parameter [{}] to AWS SSM. Endpoint connection failed! Did you configure the AWS region correctly?".format(param_name))
            return None

    #####################################################################################
    def read_app_parameter(self, param_name: str) -> str:
        self.flask_app.logger.debug("Now reading application parameter [{}] in AWS SSM.".format(param_name))

        param_data = None
        try:
            ssm_result = self.aws_ssm_client.get_parameter(Name = param_name)
            param_data = ssm_result["Parameter"]
            self.flask_app.logger.debug(
                "Reading application parameter [{}] result = [{}]".format(param_name, param_data))
        except botocore.exceptions.NoCredentialsError:
            self.flask_app.logger.error(
                "Could not read application parameter [{}] from AWS SSM. No credentials found. Did you configure the AWS credentials Key and SecretKey?".format(param_name, param_data))
            return None
        except botocore.exceptions.EndpointConnectionError:
            self.flask_app.logger.error(
                "Could not read application parameter [{}] from AWS SSM. Endpoint connection failed! Did you configure the AWS region correctly?".format(param_name, param_data))
            return None
        #except 
        #    self.flask_app.logger.error("Could not read application parameter [{}] from AWS SSM. Parameter does not exist in SSM. Was the AWS envrionment set up correctly?".format(param_name, param_data))
        #    return None

        return param_data["Value"]

        