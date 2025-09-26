#!/usr/bin/env python3
"""
Script para hacer pruebas de las funciones Lambda localmente
"""

import sys
import os
import json
from datetime import datetime

# Agregar el directorio lambdas al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambdas'))

import create_task
import list_tasks
import update_task
import delete_task
import upload_file
import process_sqs
import process_s3_event

def test_create_task():
    """Probar creación de tarea"""
    print("=== Probando creación de tarea ===")
    
    event = {
        'body': json.dumps({
            'title': 'Tarea de prueba',
            'description': 'Esta es una tarea creada durante las pruebas',
            'priority': 'high',
            'tags': ['prueba', 'desarrollo'],
            'due_date': '2024-01-20T15:00:00'
        })
    }
    
    result = create_task.lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 201:
        response_data = json.loads(result['body'])
        task_id = response_data['task']['id']
        print(f"Tarea creada con ID: {task_id}")
        return task_id
    else:
        print(f"Error: {result['body']}")
        return None

def test_list_tasks():
    """Probar listado de tareas"""
    print("\n=== Probando listado de tareas ===")
    
    event = {
        'queryStringParameters': {
            'limit': '10'
        }
    }
    
    result = list_tasks.lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        response_data = json.loads(result['body'])
        tasks = response_data.get('tasks', [])
        print(f"Tareas encontradas: {len(tasks)}")
        for task in tasks[:3]:  # Mostrar primeras 3
            print(f"  - {task['title']} ({task['status']})")
        return tasks
    else:
        print(f"Error: {result['body']}")
        return []

def test_update_task(task_id):
    """Probar actualización de tarea"""
    print(f"\n=== Probando actualización de tarea {task_id} ===")
    
    if not task_id:
        print("No hay task_id para actualizar")
        return
    
    event = {
        'pathParameters': {'id': task_id},
        'body': json.dumps({
            'status': 'in_progress',
            'description': 'Tarea actualizada durante las pruebas'
        })
    }
    
    result = update_task.lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        response_data = json.loads(result['body'])
        print(f"Tarea actualizada: {response_data['task']['title']}")
    else:
        print(f"Error: {result['body']}")

def test_upload_file(task_id):
    """Probar subida de archivo"""
    print(f"\n=== Probando subida de archivo para tarea {task_id} ===")
    
    if not task_id:
        print("No hay task_id para subir archivo")
        return
    
    import base64
    
    # Crear archivo de prueba
    test_content = "Este es un archivo de prueba para la tarea."
    encoded_content = base64.b64encode(test_content.encode()).decode()
    
    event = {
        'pathParameters': {'id': task_id},
        'body': json.dumps({
            'file_content': encoded_content,
            'file_name': 'archivo_prueba.txt',
            'content_type': 'text/plain'
        })
    }
    
    result = upload_file.lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 201:
        response_data = json.loads(result['body'])
        print(f"Archivo subido: {response_data['file_url']}")
    else:
        print(f"Error: {result['body']}")

def test_sqs_processing():
    """Probar procesamiento de mensajes SQS"""
    print("\n=== Probando procesamiento SQS ===")
    
    event = {
        'Records': [
            {
                'messageId': 'test-msg-1',
                'body': json.dumps({
                    'action': 'process_new_task',
                    'task_id': 'test-task-123',
                    'task_data': {
                        'title': 'Tarea desde SQS',
                        'status': 'pending'
                    }
                })
            }
        ]
    }
    
    result = process_sqs.lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    print(f"Resultado: {result['body']}")

def test_s3_event_processing():
    """Probar procesamiento de eventos S3"""
    print("\n=== Probando procesamiento de eventos S3 ===")
    
    event = {
        'Records': [
            {
                'eventSource': 'aws:s3',
                'eventName': 'ObjectCreated:Put',
                's3': {
                    'bucket': {
                        'name': 'task-manager-files'
                    },
                    'object': {
                        'key': 'bulk-upload/test-tasks.csv'
                    }
                }
            }
        ]
    }
    
    result = process_s3_event.lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    print(f"Resultado: {result['body']}")

def test_delete_task(task_id):
    """Probar eliminación de tarea"""
    print(f"\n=== Probando eliminación de tarea {task_id} ===")
    
    if not task_id:
        print("No hay task_id para eliminar")
        return
    
    # Esperar confirmación para no eliminar accidentalmente
    confirm = input("¿Eliminar la tarea de prueba? (y/N): ")
    if confirm.lower() != 'y':
        print("Eliminación cancelada")
        return
    
    event = {
        'pathParameters': {'id': task_id}
    }
    
    result = delete_task.lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        response_data = json.loads(result['body'])
        print(f"Resultado: {response_data['message']}")
    else:
        print(f"Error: {result['body']}")

def main():
    """Ejecutar todas las pruebas"""
    print("=== Iniciando pruebas de funciones Lambda ===\n")
    
    try:
        # Probar creación de tarea
        task_id = test_create_task()
        
        # Probar listado
        tasks = test_list_tasks()
        
        # Si no se creó tarea nueva pero hay tareas existentes, usar la primera
        if not task_id and tasks:
            task_id = tasks[0]['id']
            print(f"Usando tarea existente para pruebas: {task_id}")
        
        # Probar actualización
        if task_id:
            test_update_task(task_id)
            test_upload_file(task_id)
        
        # Probar procesamiento de mensajes
        test_sqs_processing()
        test_s3_event_processing()
        
        # Probar eliminación (opcional)
        if task_id:
            test_delete_task(task_id)
        
        print("\n=== Pruebas completadas ===")
        
    except Exception as e:
        print(f"\nError durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()