from flask import (
    Flask, 
    request, 
    jsonify, 
    Response
)
import logging
from http import HTTPStatus
import boto3
import os

#####################################################################################
class DpsWebApiServiceBase:
    # Global constants
    app_prefix = os.getenv('DPS_PREFIX')
    service_version = os.getenv('DPS_VERSION')

    # Dynamic data
    flask_app: Flask
    service_name: str    
    service_route_prefix: str
    service_log_prefix: str    

    # application parameters
    sys_param_log_level = "/" + app_prefix + "/system/logging/log-level"

    # aws client instances
    aws_ssm_client = boto3.client('ssm')

    #####################################################################################
    def __init__(self, flask_app: Flask, service_name: str, service_route: str) -> None:
        self.flask_app = flask_app
        self.service_name = service_name        
        self.service_route_prefix = "/" + self.service_version + service_route
        
        ## SET SOME LOGGING SETTINGS        
        logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s')
        self.flask_app.logger.setLevel("INFO")
        self.service_log_prefix = service_name + ": "

        self.log("STARTING UP. app_prefix = [" + self.app_prefix + "], service_version = [" + self.service_version + "], service_route = [" + self.service_route + "]")
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
    def log(self, msg: object, *args: object) -> None:
        
        curr_log_level = self.flask_app.logger.getEffectiveLevel()
        message = self.service_log_prefix + format(msg, args)
        
        if curr_log_level == logging.INFO :
            self.flask_app.logger.info(message)
        elif curr_log_level == logging.WARNING :
            self.flask_app.logger.warn(message)
        elif curr_log_level == logging.ERROR :
            self.flask_app.logger.error(message)
        else :
            self.flask_app.logger.debug(message)

    #####################################################################################
    def handle_health_check(self) -> Response:
        self.log("Handling health check...")

        # read global parameters and update local data
        param_log_level = self.read_app_parameter(self.sys_param_log_level)
        self.flask_app.logger.setLevel(param_log_level)

        # Provide status response
        response_set.status = HTTPStatus.OK
        response_set = jsonify(
            result = response_set.status, 
            message = "Health Check OK!", 
            hints = "Service [" + self.service_name + "]") 
        
        return response_set

    #####################################################################################
    def write_app_parameter(self, param_name: str, new_value: str) -> None:
        self.log("Now updating application parameter [" + param_name + "] in AWS SSM with value: [" + new_value + "]")
        self.aws_ssm_client.put_parameter(
            Name = param_name,
            Value = new_value,
            Overwrite = True,
            Type = "String",
            Tier = "Standard"
        )

    #####################################################################################
    def read_app_parameter(self, param_name: str) -> str:
        self.log("Now reading application parameter [" + param_name + "] in AWS SSM...")
        ssm_result = self.aws_ssm_client.get_parameter(Name = param_name)
        param_data = ssm_result["Parameter"]
        self.log("Reading application parameter [" + param_name + "] result = " + param_data)
        return param_data["Value"]

        