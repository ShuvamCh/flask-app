# flask-app

ChatGPT
Sure, let's create a practical example step-by-step for a simple Node.js application.

1. Create a GitHub Repository
Create a new GitHub repository named nodejs-app.

2. Dockerize Your Application
Create a simple Node.js application with the following structure:

css
Copy code
nodejs-app/
│
├── Dockerfile
├── app.js
├── package.json
└── .github/
    └── workflows/
        └── main.yml
app.js:
javascript
Copy code
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});
package.json:
json
Copy code
{
  "name": "nodejs-app",
  "version": "1.0.0",
  "main": "app.js",
  "scripts": {
    "start": "node app.js"
  },
  "dependencies": {
    "express": "^4.17.1"
  }
}
Dockerfile:
Dockerfile
Copy code
FROM node:14

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000
CMD ["node", "app.js"]
3. AWS Setup
Create an ECR Repository:

Navigate to the ECR section in the AWS Management Console.
Create a new repository named nodejs-app.
Create an ECS Cluster:

Navigate to the ECS section in the AWS Management Console.
provide a practical example of the same where scripting is done via python
ChatGPT
Let's set up an end-to-end GitHub Actions CI/CD pipeline that builds a Docker image and deploys a Python Flask application to AWS. We'll use a Python script to handle the deployment steps.

Step-by-Step Guide
1. Create a GitHub Repository
Create a new GitHub repository named flask-app.

2. Create the Flask Application
Create a simple Flask application with the following structure:

css
Copy code
flask-app/
│
├── app/
│   ├── __init__.py
│   └── main.py
├── Dockerfile
├── requirements.txt
├── ecs_deploy.py
└── .github/
    └── workflows/
        └── main.yml
app/__init__.py:
python
Copy code
from flask import Flask

app = Flask(__name__)

from app import main
app/main.py:
python
Copy code
from app import app

@app.route('/')
def hello_world():
    return 'Hello, World!'
requirements.txt:
makefile
Copy code
Flask==2.0.2
Dockerfile:
Dockerfile
Copy code
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app/main.py"]
3. Create the Deployment Script
Create a script ecs_deploy.py to handle the deployment to AWS ECS.

ecs_deploy.py:
python
Copy code
import boto3
import os
import json

def get_latest_image_uri(repository_name):
    client = boto3.client('ecr')
    response = client.describe_images(
        repositoryName=repository_name,
        filter={'tagStatus': 'TAGGED'}
    )
    image_details = sorted(response['imageDetails'], key=lambda x: x['imagePushedAt'], reverse=True)
    return image_details[0]['imageTags'][0]

def update_ecs_service(cluster_name, service_name, image_uri):
    client = boto3.client('ecs')
    response = client.describe_task_definition(taskDefinition=service_name)
    task_definition = response['taskDefinition']

    container_definitions = task_definition['containerDefinitions']
    for container in container_definitions:
        container['image'] = image_uri

    response = client.register_task_definition(
        family=task_definition['family'],
        taskRoleArn=task_definition['taskRoleArn'],
        executionRoleArn=task_definition['executionRoleArn'],
        networkMode=task_definition['networkMode'],
        containerDefinitions=container_definitions,
        volumes=task_definition['volumes'],
        placementConstraints=task_definition['placementConstraints'],
        requiresCompatibilities=task_definition['requiresCompatibilities'],
        cpu=task_definition['cpu'],
        memory=task_definition['memory']
    )

    new_task_definition_arn = response['taskDefinition']['taskDefinitionArn']

    client.update_service(
        cluster=cluster_name,
        service=service_name,
        taskDefinition=new_task_definition_arn
    )

if __name__ == "__main__":
    repository_name = os.getenv('ECR_REPOSITORY_NAME')
    cluster_name = os.getenv('ECS_CLUSTER_NAME')
    service_name = os.getenv('ECS_SERVICE_NAME')
    image_tag = os.getenv('IMAGE_TAG', 'latest')

    image_uri = f"{repository_name}:{image_tag}"
    update_ecs_service(cluster_name, service_name, image_uri)
4. Create GitHub Secrets
Store the necessary AWS credentials and other sensitive information as GitHub Secrets:

AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
ECR_REPOSITORY_NAME
ECS_CLUSTER_NAME
ECS_SERVICE_NAME
5. Set Up GitHub Actions Workflow
Create a .github/workflows/main.yml file in your repository to define the CI/CD pipeline.

.github/workflows/main.yml:
yaml
Copy code
name: CI/CD Pipeline

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      - name: Log in to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build Docker image
        run: |
          IMAGE_TAG=latest
          docker build -t ${{ secrets.ECR_REPOSITORY_NAME }}:${IMAGE_TAG} .
          echo "IMAGE_TAG=${IMAGE_TAG}" >> $GITHUB_ENV

      - name: Push Docker image to Amazon ECR
        run: |
          docker push ${{ secrets.ECR_REPOSITORY_NAME }}:${{ env.IMAGE_TAG }}

      - name: Install AWS CLI
        run: |
          pip install boto3

      - name: Deploy to Amazon ECS
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: ${{ secrets.AWS_REGION }}
          ECR_REPOSITORY_NAME: ${{ secrets.ECR_REPOSITORY_NAME }}
          ECS_CLUSTER_NAME: ${{ secrets.ECS_CLUSTER_NAME }}
          ECS_SERVICE_NAME: ${{ secrets.ECS_SERVICE_NAME }}
          IMAGE_TAG: ${{ env.IMAGE_TAG }}
        run: |
          python ecs_deploy.py
Explanation of the Workflow Steps:
Checkout code: Uses the actions/checkout@v2 action to check out the repository.
Set up Python: Uses the actions/setup-python@v2 action to set up a Python environment.
Log in to Amazon ECR: Uses the aws-actions/amazon-ecr-login@v1 action to log in to Amazon ECR.
Build Docker image: Builds the Docker image using the docker build command.
Push Docker image to Amazon ECR: Pushes the Docker image to your Amazon ECR repository.
Install AWS CLI: Installs the AWS CLI and boto3 library.
Deploy to Amazon ECS: Runs the ecs_deploy.py script to update the ECS service with the new image.
Security Note:
Ensure your secrets are managed properly and avoid hardcoding any sensitive information in your repository.

With this setup, every time you push code to the main branch, GitHub Actions will build your Docker image, push it to ECR, and update your ECS service to use the new image, achieving an end-to-end CI/CD pipeline.
