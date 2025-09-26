#!/usr/bin/env python3
"""
Script para configurar los recursos AWS en LocalStack para desarrollo local
"""

import boto3
import json
import time
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de LocalStack
LOCALSTACK_ENDPOINT = "http://localhost:4566"
AWS_REGION = "us-east-1"

def get_client(service_name):
    return boto3.client(
        service_name,
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name=AWS_REGION
    )

def get_resource(service_name):
    return boto3.resource(
        service_name,
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name=AWS_REGION
    )

def create_dynamodb_table():
    """Crear tabla DynamoDB para tareas"""
    print("Creando tabla DynamoDB...")
    
    dynamodb = get_resource('dynamodb')
    
    table_name = 'tasks-table'
    
    try:
        # Verificar si la tabla ya existe
        table = dynamodb.Table(table_name)
        table.load()
        print(f"Tabla {table_name} ya existe")
        return
    except:
        pass
    
    # Crear tabla
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Esperar a que la tabla esté activa
    table.wait_until_exists()
    print(f"Tabla {table_name} creada exitosamente")

def create_s3_bucket():
    """Crear bucket S3 para archivos"""
    print("Creando bucket S3...")
    
    s3 = get_client('s3')
    bucket_name = 'task-manager-files'
    
    try:
        # Verificar si el bucket ya existe
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} ya existe")
        return
    except:
        pass
    
    # Crear bucket
    s3.create_bucket(Bucket=bucket_name)
    print(f"Bucket {bucket_name} creado exitosamente")
    
    # Crear algunas carpetas de ejemplo
    folders = [
        'tasks/',
        'bulk-upload/',
        'reports/',
        'reports/csv-processing/'
    ]
    
    for folder in folders:
        s3.put_object(Bucket=bucket_name, Key=folder)
    
    print("Estructura de carpetas creada en S3")

def create_sqs_queue():
    """Crear cola SQS para procesamiento en background"""
    print("Creando cola SQS...")
    
    sqs = get_client('sqs')
    queue_name = 'task-queue'
    
    try:
        # Crear cola
        response = sqs.create_queue(
            QueueName=queue_name,
            Attributes={
                'VisibilityTimeout': '300',
                'MessageRetentionPeriod': '1209600',  # 14 días
                'ReceiveMessageWaitTimeSeconds': '20'  # Long polling
            }
        )
        
        queue_url = response['QueueUrl']
        print(f"Cola SQS creada: {queue_url}")
        
        return queue_url
        
    except Exception as e:
        if 'QueueAlreadyExists' in str(e):
            # Obtener URL de cola existente
            response = sqs.get_queue_url(QueueName=queue_name)
            queue_url = response['QueueUrl']
            print(f"Cola SQS ya existe: {queue_url}")
            return queue_url
        else:
            raise e

def create_sns_topic():
    """Crear tópico SNS para notificaciones"""
    print("Creando tópico SNS...")
    
    sns = get_client('sns')
    topic_name = 'task-notifications'
    
    try:
        # Crear tópico
        response = sns.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        print(f"Tópico SNS creado: {topic_arn}")
        
        # Suscribir un endpoint de email (opcional para desarrollo)
        # sns.subscribe(
        #     TopicArn=topic_arn,
        #     Protocol='email',
        #     Endpoint='test@example.com'
        # )
        
        return topic_arn
        
    except Exception as e:
        print(f"Error creando tópico SNS: {str(e)}")
        return None

def create_sample_csv():
    """Crear archivo CSV de ejemplo para pruebas"""
    print("Creando archivo CSV de ejemplo...")
    
    csv_content = """title,description,status,priority,due_date,tags
Revisar documentación,Revisar y actualizar la documentación del proyecto,pending,high,2024-01-15T10:00:00,documentación,revisión
Implementar autenticación,Agregar sistema de autenticación de usuarios,pending,critical,2024-01-20T15:30:00,seguridad,backend
Diseño de UI,Crear mockups para la nueva interfaz,in_progress,medium,2024-01-18T12:00:00,diseño,frontend
Testing unitario,Escribir pruebas unitarias para módulos principales,pending,medium,,testing,calidad
Deploy producción,Desplegar versión estable a producción,pending,critical,2024-01-25T09:00:00,deploy,producción"""
    
    # Guardar en bucket S3
    s3 = get_client('s3')
    bucket_name = 'task-manager-files'
    
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key='bulk-upload/sample-tasks.csv',
            Body=csv_content,
            ContentType='text/csv'
        )
        print("Archivo CSV de ejemplo creado en S3: bulk-upload/sample-tasks.csv")
    except Exception as e:
        print(f"Error creando archivo CSV: {str(e)}")

def update_env_file(queue_url, topic_arn):
    """Actualizar archivo .env con URLs reales"""
    print("Actualizando archivo .env...")
    
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    env_content = f"""# Variables de entorno para desarrollo local
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=tasks-table
S3_BUCKET_NAME=task-manager-files
SQS_QUEUE_URL={queue_url}
SNS_TOPIC_ARN={topic_arn}

# Para LocalStack
LOCALSTACK_ENDPOINT=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"Archivo .env actualizado en: {env_path}")

def main():
    """Configurar todos los recursos AWS en LocalStack"""
    print("=== Configurando entorno local con LocalStack ===\n")
    
    # Esperar a que LocalStack esté listo
    print("Esperando a que LocalStack esté listo...")
    time.sleep(5)
    
    try:
        # Crear recursos
        create_dynamodb_table()
        create_s3_bucket()
        queue_url = create_sqs_queue()
        topic_arn = create_sns_topic()
        create_sample_csv()
        
        # Actualizar archivo .env
        update_env_file(queue_url, topic_arn)
        
        print("\n=== Configuración completada exitosamente ===")
        print("\nRecursos creados:")
        print(f"- DynamoDB: tasks-table")
        print(f"- S3: task-manager-files")
        print(f"- SQS: {queue_url}")
        print(f"- SNS: {topic_arn}")
        
        print("\nPara iniciar el servidor API local, ejecuta:")
        print("cd local && python api_server.py")
        
    except Exception as e:
        print(f"Error durante la configuración: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())