#!/usr/bin/env python3
"""
Pruebas básicas para verificar que la implementación funciona
"""

import sys
import os
import json

# Agregar el directorio lambdas al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lambdas'))

def test_models():
    """Probar que los modelos se pueden importar y crear"""
    print("🧪 Probando modelos...")
    try:
        from models import TaskCreate, TaskUpdate, TaskStatus, TaskPriority
        
        # Crear una tarea de prueba
        task_data = {
            'title': 'Tarea de prueba',
            'description': 'Esta es una tarea de prueba',
            'priority': 'high',
            'tags': ['test', 'basic']
        }
        
        task = TaskCreate(**task_data)
        print(f"✅ TaskCreate creado: {task.title}")
        
        # Probar TaskUpdate
        update_data = {'status': 'completed'}
        task_update = TaskUpdate(**update_data)
        print(f"✅ TaskUpdate creado: {task_update.status}")
        
        return True
    except Exception as e:
        print(f"❌ Error en modelos: {str(e)}")
        return False

def test_create_task_handler():
    """Probar el handler de crear tarea"""
    print("\n🧪 Probando create_task_handler...")
    try:
        from handlers.create_task_handler import lambda_handler
        
        event = {
            'body': json.dumps({
                'title': 'Tarea desde prueba',
                'description': 'Descripción de prueba',
                'priority': 'medium'
            })
        }
        
        result = lambda_handler(event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 201:
            body = json.loads(result['body'])
            print(f"✅ Tarea creada: {body.get('message', 'Sin mensaje')}")
            return True
        else:
            print(f"❌ Error: {result.get('body', 'Sin detalles')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en create_task_handler: {str(e)}")
        return False

def test_list_tasks_handler():
    """Probar el handler de listar tareas"""
    print("\n🧪 Probando list_tasks_handler...")
    try:
        from handlers.list_tasks_handler import lambda_handler
        
        event = {
            'queryStringParameters': {'limit': '10'}
        }
        
        result = lambda_handler(event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            tasks_count = len(body.get('tasks', []))
            print(f"✅ Tareas encontradas: {tasks_count}")
            return True
        else:
            print(f"❌ Error: {result.get('body', 'Sin detalles')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en list_tasks_handler: {str(e)}")
        return False

def test_task_service():
    """Probar el servicio de tareas"""
    print("\n🧪 Probando TaskService...")
    try:
        from services.task_service import TaskService
        from models import TaskCreate
        
        service = TaskService()
        
        # Crear tarea
        task_data = TaskCreate(
            title='Tarea desde servicio',
            description='Prueba del servicio',
            priority='low'
        )
        
        task = service.create_task(task_data)
        print(f"✅ Tarea creada por servicio: {task.title}")
        
        # Listar tareas
        tasks = service.list_tasks(limit=5)
        print(f"✅ Tareas listadas: {len(tasks)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en TaskService: {str(e)}")
        return False

def main():
    """Ejecutar todas las pruebas básicas"""
    print("🚀 Iniciando pruebas básicas del Task Manager")
    print("=" * 50)
    
    tests = [
        test_models,
        test_create_task_handler,
        test_list_tasks_handler,
        test_task_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas básicas pasaron!")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron")
        return 1

if __name__ == "__main__":
    exit(main())