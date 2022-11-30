# Data Provider Service for AWS

This is a prototype implementation of an AWS based data provider service.
It implements a micro-service architecture with Python services on AWS Fargate, which are running in private VPC subnets. A puplic ALB at their front, routing traffic to the Fargate services based by Path. It is auto-scaling with 2 service instances as a start.

The conceptual idea behind this project can be read here:
https://ideal-digital.org/2020/04/03/patterns-for-building-data-provider-services-on-aws/

# Requirements
This repo was created on a Ubuntu Linux with the following installed software:
 - Visual Studio Code
 - Git
 - AWS CLI
 - AWS CDK
 - Python3 + Pip3
 - Flask
 - Docker
 
See the requirements.txt files in the Python projects for specific module requirements (to be installed with Pip)

