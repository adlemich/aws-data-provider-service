from flask import Flask, Response, Request, jsonify
from http import HTTPStatus

from dps_shared.dps_web_api_service_base import DpsWebApiServiceBase

#####################################################################################
class DpsInjestEndpointsService(DpsWebApiServiceBase):

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
            hints = "{{'Service': '{}', 'Log-Level': '{}'}}".format(self.service_name, self.flask_app.logger.getEffectiveLevel())
        ) 
        response_set.status = HTTPStatus.OK
        
        return response_set

   