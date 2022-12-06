from flask import Flask
from dps_injest_endpoints_service import DpsInjestEndpointsService

############################################################################
## Create Flask application and our implementation service class
############################################################################
app = Flask(__name__)
api_svc = DpsInjestEndpointsService(
    flask_app = app, 
    service_name = "dps-injest-endpoints-svc",
    service_route = "/ingest-endpoints")

############################################################################
## GET          /
############################################################################
@app.route("/", methods=['GET'])
def get_root():
    
    # This is called by the AWS Application Load Balancer for health checks
    return api_svc.handle_health_check()

############################################################################
## GET          /ingest-endpoints
############################################################################
@app.route(api_svc.get_service_route_prefix() + "/", methods = ['GET'])
def get_hello():
        
    # This is the root of this api service, provide public status information
    return api_svc.get_status()


##-------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port = 5002)