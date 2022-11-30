from flask import Flask, request
import os

from dps_administration_service import DpsAdministrationService

############################################################################
## Create Flask application and our implementation service class
############################################################################
app = Flask(__name__)
api_svc = DpsAdministrationService(
    flask_app = app, 
    service_name = "dps-administration-svc",
    service_route = "/admin")

############################################################################
## GET          /
############################################################################
@app.route("/", methods=['GET'])
def get_root():
    
    # This is called by the AWS Application Load Balancer for health checks
    return api_svc.handle_health_check()

############################################################################
## GET          /admin
############################################################################
@app.route(api_svc.get_service_route_prefix() + "/", methods = ['GET'])
def get_hello():
        
    # This is the root of this api service, provide public status information
    return api_svc.get_status()

############################################################################
## PUT          /admin/log-level
############################################################################
@app.route(api_svc.get_service_route_prefix() + "/log-level", methods = ['PUT'])
def set_log_level():

    # This is called to change the log level of the backend service
    return api_svc.put_log_level(request)    

##-------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port = 5001)