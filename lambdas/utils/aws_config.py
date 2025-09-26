import boto3
import os
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class AWSConfig:
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.localstack_endpoint = os.getenv('LOCALSTACK_ENDPOINT')
        self.use_localstack = self.localstack_endpoint is not None
        
        # Configuración para LocalStack (desarrollo local)
        if self.use_localstack:
            self.aws_config = {
                'endpoint_url': self.localstack_endpoint,
                'aws_access_key_id': 'test',
                'aws_secret_access_key': 'test',
                'region_name': self.region
            }
        else:
            # Configuración para AWS real
            self.aws_config = {
                'region_name': self.region
            }
    
    def get_dynamodb_client(self):
        return boto3.client('dynamodb', **self.aws_config)
    
    def get_dynamodb_resource(self):
        return boto3.resource('dynamodb', **self.aws_config)
    
    def get_s3_client(self):
        return boto3.client('s3', **self.aws_config)
    
    def get_sqs_client(self):
        return boto3.client('sqs', **self.aws_config)
    
    def get_sns_client(self):
        return boto3.client('sns', **self.aws_config)


# Instancia global
aws_config = AWSConfig()


# Funciones de utilidad
def get_table_name():
    return os.getenv('DYNAMODB_TABLE_NAME', 'tasks-table')


def get_bucket_name():
    return os.getenv('S3_BUCKET_NAME', 'task-manager-files')


def get_queue_url():
    return os.getenv('SQS_QUEUE_URL', '')


def get_topic_arn():
    return os.getenv('SNS_TOPIC_ARN', '')