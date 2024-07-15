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
