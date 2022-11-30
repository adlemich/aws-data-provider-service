from flask import Flask, request, jsonify, Response
import logging
import json

app = Flask(__name__)

## GLOBAL SETTINGS
service_name = "dps-administration-svc"
service_version = "v001"
service_route_prefix = "/" + service_version + "/admin"

## SET SOME LOGGING SETTINGS
############################################################################
logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s')
app.logger.setLevel("INFO")
service_log_prefix = service_name + ": " 

############################################################################
@app.route("/", methods=['GET'])
def get_root():
    # This is called by the AWS Application Load Balancer for health checks
    app.logger.debug("dps-ingest-endpoint-svc: Handling <GET> on path </>")
    
    return "Health Check OK"

############################################################################
## /admin     GET
############################################################################
@app.route(service_route_prefix + "/", methods = ['GET'])
def get_hello():
        
    app.logger.debug(service_log_prefix + "Handling method <GET> on path <" + service_route_prefix + "/>")
    
    response_set = jsonify(result = 200, message = "OK", hints = "Hello World from " + service_name) 
    response_set.status = 200

    return response_set

############################################################################
## /admin/log-level         PUT
############################################################################
@app.route(service_route_prefix + "/log-level", methods = ['PUT'])
def set_log_level():
    # This is called to change the log level of the backend service
    app.logger.debug(service_log_prefix + "Handling method <PUT> on path <" + service_route_prefix + "/log-level>")
    
    # We expect JSON payload like this: {"log-level": "DEBUG"}
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response("Content-Type not supported! Only 'application/json' is accepted.", status = 400) 

    new_log_level = "n/a"
    new_log_level = request.json["log-level"]
    app.logger.debug(service_log_prefix + "Client request to change log level to: <" + new_log_level + ">")
    
    match_ok = True
    if new_log_level == "DEBUG":
            app.logger.setLevel(logging.DEBUG)
    elif new_log_level == "INFO":
            app.logger.setLevel(logging.INFO)
    elif new_log_level == "WARNING":
            app.logger.setLevel(logging.WARNING)
    elif new_log_level ==  "ERROR":
            app.logger.setLevel(logging.ERROR)
    else:
            match_ok = False

    # Check result and compose answer
    result_ = 200 #OK
    message_ = "OK"
    hints_ = ""

    if not match_ok:
        result_ = 400 #Bad request
        message_ = "Error! Requested new log level <" + new_log_level + "> is not a valid input."
        hints_ = "This method expects a JSON body with format: " + \
            json.dumps({'log-level': 'DEBUG'}) +  \
            ". Parameters: log-level [IN, string]: valid values are 'DEBUG', 'INFO', 'WARNING', 'ERROR'."

    response_set = jsonify(result = result_, message = message_, hints = hints_) 
    response_set.status = result_

    return response_set

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port = 5001)