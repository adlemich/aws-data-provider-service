from flask import Flask, Response, Request, jsonify
from http import HTTPStatus
import logging
import json

from dps_web_api_service_base import DpsWebApiServiceBase

#####################################################################################
class DpsAdministrationService(DpsWebApiServiceBase):

    #####################################################################################
    def __init__(self, flask_app: Flask, service_name: str, service_route: str) -> None:
        super().__init__(flask_app, service_name, service_route)

        return

    #####################################################################################
    def get_status(self) -> Response:
        self.flask_app.logger.debug("Handling get Status...")

        response_set = jsonify(
            result = HTTPStatus.OK, 
            message = "API service status OK!", 
            hints = "{ 'Service': '" + self.service_name + "'," + \
                "'Log-Level': '" + self.flask_app.logger.getEffectiveLevel() + "'" +  \
                " }"
        ) 
        response_set.status = HTTPStatus.OK
        
        return response_set

    #####################################################################################
    def put_log_level(self, request: Request) -> Response:
        self.flask_app.logger.debug("Handling put_log_level...")

        response_set = jsonify(
            result = HTTPStatus.OK, 
            message = "OK", 
            hints = ""
        ) 
        response_set.status = HTTPStatus.OK

        # We expect JSON payload like this: {"log-level": "DEBUG"}
        content_type = request.headers.get('Content-Type')
        if (content_type != 'application/json'):
            response_set = jsonify(
                result = HTTPStatus.BAD_REQUEST, 
                message = "Content-Type not supported! Only [application/json] is accepted.", 
                hints = ""
            )
            response_set.status = HTTPStatus.BAD_REQUEST
            return response_set 

        new_log_level = "n/a"
        new_log_level = request.json["log-level"]
        self.flask_app.logger.debug("Client request to change system log level to: [" + new_log_level + "]")
        
        # Set new level locally and in the AWS parameter store
        match_ok = True
        
        if new_log_level == "DEBUG":
                self.flask_app.logger.setLevel(logging.DEBUG)
        elif new_log_level == "INFO":
                self.flask_app.logger.setLevel(logging.INFO)
        elif new_log_level == "WARNING":
                self.flask_app.logger.setLevel(logging.WARNING)
        elif new_log_level ==  "ERROR":
                self.flask_app.logger.setLevel(logging.ERROR)
        else:
                match_ok = False
                self.flask_app.logger.debug("Provided input: [" + new_log_level + "] was not recognized, will ignore and generate an error response.")
        
        # Check result and compose answer
        if not match_ok:
            response_set.status = HTTPStatus.BAD_REQUEST #Bad request
            message_ = "Error! Requested new log level [" + new_log_level + "] is not a valid input."
            hints_ = "This method expects a JSON body with format: " + \
                json.dumps({'log-level': 'DEBUG'}) +  \
                ". Parameters: log-level [IN, string]: valid values are 'DEBUG', 'INFO', 'WARNING', 'ERROR'."
            response_set = jsonify(result = response_set.status, message = message_, hints = hints_) 
        else :
            # update AWS SSM Parameter for all services
            self.write_app_parameter(self.sys_param_log_level, new_log_level)

        return response_set        