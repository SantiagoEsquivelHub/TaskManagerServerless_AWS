#!/usr/bin/env python3
"""
Script de prueba rápida para verificar que los handlers funcionan
"""

import sys
import os
import json
from datetime import datetime

# Configurar el PYTHONPATH para que incluya el directorio lambdas
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
lambdas_path = os.path.join(project_root, 'lambdas')

# Agregar múltiples rutas para asegurar que funcione
sys.path.insert(0, lambdas_path)
sys.path.insert(0, project_root)

print(f"🔧 Configuración de rutas:")
print(f"   - Directorio actual: {current_dir}")
print(f"   - Directorio del proyecto: {project_root}")
print(f"   - Directorio lambdas: {lambdas_path}")
print(f"   - PYTHONPATH incluye: {lambdas_path}")
print()

def test_imports():
    """Probar que todos los imports funcionan"""
    print("🔍 Probando imports...")
    
    try:
        from models import TaskCreate, Task, TaskStatus, TaskPriority
        print("✅ Models importados correctamente")
        
        from utils.aws_config import aws_config
        print("✅ AWS Config importado correctamente")
        
        from repositories.task_repository import TaskRepository
        print("✅ Task Repository importado correctamente")
        
        from services.task_service import TaskService
        print("✅ Task Service importado correctamente")
        
        from handlers.create_task_handler import lambda_handler as create_handler
        print("✅ Create Handler importado correctamente")
        
        from handlers.list_tasks_handler import lambda_handler as list_handler
        print("✅ List Handler importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_task_model():
    """Probar que los modelos funcionan"""
    print("\n📋 Probando modelos...")
    
    try:
        from models import TaskCreate, TaskStatus, TaskPriority
        
        # Crear TaskCreate
        task_data = {
            'title': 'Tarea de prueba',
            'description': 'Esta es una prueba del modelo',
            'priority': 'high',
            'tags': ['prueba', 'local']
        }
        
        task_create = TaskCreate(**task_data)
        print(f"✅ TaskCreate creado: {task_create.title}")
        print(f"   - Status por defecto: {task_create.status}")
        print(f"   - Priority: {task_create.priority}")
        print(f"   - Tags: {task_create.tags}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en modelos: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_create_handler():
    """Probar el handler de crear tarea"""
    print("\n🚀 Probando Create Task Handler...")
    
    try:
        from handlers.create_task_handler import lambda_handler
        
        # Evento de prueba
        event = {
            'body': json.dumps({
                'title': 'Mi primera tarea de prueba',
                'description': 'Esta es una tarea creada durante las pruebas locales',
                'priority': 'high',
                'tags': ['prueba', 'desarrollo', 'local']
            })
        }
        
        print("📤 Enviando evento al handler...")
        result = lambda_handler(event, None)
        
        print(f"📨 Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 201:
            response_data = json.loads(result['body'])
            print(f"✅ Tarea creada exitosamente!")
            print(f"   - ID: {response_data['task']['id']}")
            print(f"   - Título: {response_data['task']['title']}")
            print(f"   - Status: {response_data['task']['status']}")
            return response_data['task']['id']
        else:
            print(f"❌ Error: {result['body']}")
            return None
            
    except Exception as e:
        print(f"❌ Error en handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_list_handler():
    """Probar el handler de listar tareas"""
    print("\n📋 Probando List Tasks Handler...")
    
    try:
        from handlers.list_tasks_handler import lambda_handler
        
        # Evento de prueba
        event = {
            'queryStringParameters': {
                'limit': '5'
            }
        }
        
        print("📤 Enviando evento al handler...")
        result = lambda_handler(event, None)
        
        print(f"📨 Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            response_data = json.loads(result['body'])
            tasks = response_data.get('tasks', [])
            print(f"✅ Tareas listadas exitosamente!")
            print(f"   - Encontradas: {len(tasks)} tareas")
            
            for i, task in enumerate(tasks[:3], 1):  # Mostrar primeras 3
                print(f"   {i}. {task['title']} ({task['status']})")
            
            return True
        else:
            print(f"❌ Error: {result['body']}")
            return False
            
    except Exception as e:
        print(f"❌ Error en handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🧪 === INICIANDO PRUEBAS LOCALES ===\n")
    
    # Verificar imports
    if not test_imports():
        print("\n❌ Las pruebas fallaron en imports")
        return 1
    
    # Probar modelos
    if not test_task_model():
        print("\n❌ Las pruebas fallaron en modelos")
        return 1
    
    # Nota: Los handlers necesitan AWS (LocalStack) para funcionar
    print("\n⚠️  Para probar handlers completos, necesitas LocalStack ejecutándose")
    print("   Los handlers requieren DynamoDB, S3, SQS, SNS")
    
    # Opcional: Probar handlers si LocalStack está disponible
    try:
        import requests
        response = requests.get("http://localhost:4566/_localstack/health", timeout=2)
        if response.status_code == 200:
            print("✅ LocalStack detectado, probando handlers...")
            
            task_id = test_create_handler()
            if task_id:
                test_list_handler()
        else:
            print("⚠️  LocalStack no está disponible")
    except:
        print("⚠️  LocalStack no está disponible")
    
    print("\n🎉 === PRUEBAS COMPLETADAS ===")
    return 0

if __name__ == "__main__":
    exit(main())