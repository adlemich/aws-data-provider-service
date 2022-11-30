from flask import Flask, request, jsonify, Response
import logging
import json

app = Flask(__name__)

## GLOBAL SETTINGS
service_name = "dps-provider-endpoint-svc"
service_version = "v001"
service_route_prefix = "/" + service_version + "/provider-endpoints"

## SET SOME LOGGING SETTINGS
############################################################################
logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s')
app.logger.setLevel("INFO")
service_log_prefix = service_name + ": " 

############################################################################
@app.route("/", methods=['GET'])
def get_root():
    # This is called by the AWS Application Load Balancer for health checks
    app.logger.debug(service_log_prefix + "Handling <GET> on path </>")
    
    return "Health Check OK"

############################################################################
## /provider-endpoints     GET
############################################################################
@app.route(service_route_prefix + "/", methods = ['GET'])
def get_hello():
    # This is called to change the log level of the backend service
    app.logger.debug(service_log_prefix + "Handling method <GET> on path <" + service_route_prefix + "/>")
    
    response_set = jsonify(result = 200, message = "OK", hints = "Hello World from " + service_name) 
    response_set.status = 200

    return response_set

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port = 5003)