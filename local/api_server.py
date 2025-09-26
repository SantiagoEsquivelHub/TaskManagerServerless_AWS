from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import json
import base64
import sys
import os

# Agregar el directorio lambdas al path para importar
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambdas'))

from models import TaskCreate, TaskUpdate, Task, TaskResponse
from handlers import create_task_handler
from handlers import list_tasks_handler
from handlers import update_task_handler
from handlers import delete_task_handler
from handlers import upload_file_handler
from services.task_service import TaskService

app = FastAPI(
    title="Task Manager API",
    description="API REST para gestión de tareas serverless",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Task Manager API - Funcionando localmente"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": "local"}


@app.post("/tasks", response_model=TaskResponse)
async def create_task_endpoint(task: TaskCreate):
    """Crear una nueva tarea"""
    event = {
        'body': task.json(),
        'httpMethod': 'POST'
    }
    
    response = create_task_handler.lambda_handler(event, None)
    
    if response['statusCode'] != 201:
        raise HTTPException(
            status_code=response['statusCode'],
            detail=json.loads(response['body'])
        )
    
    return json.loads(response['body'])


@app.get("/tasks", response_model=TaskResponse)
async def list_tasks_endpoint(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 50
):
    """Listar tareas con filtros opcionales"""
    query_params = {}
    if status:
        query_params['status'] = status
    if priority:
        query_params['priority'] = priority
    if tag:
        query_params['tag'] = tag
    if limit:
        query_params['limit'] = str(limit)
    
    event = {
        'queryStringParameters': query_params,
        'httpMethod': 'GET'
    }
    
    response = list_tasks_handler.lambda_handler(event, None)
    
    if response['statusCode'] != 200:
        raise HTTPException(
            status_code=response['statusCode'],
            detail=json.loads(response['body'])
        )
    
    return json.loads(response['body'])


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_endpoint(task_id: str):
    """Obtener una tarea específica"""
    # Usar el servicio para obtener la tarea
    task_service = TaskService()
    task = task_service.get_task_by_id(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return TaskResponse(message="Tarea encontrada", task=task)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(task_id: str, task_update: TaskUpdate):
    """Actualizar una tarea existente"""
    event = {
        'pathParameters': {'id': task_id},
        'body': task_update.json(exclude_unset=True),
        'httpMethod': 'PUT'
    }
    
    response = update_task_handler.lambda_handler(event, None)
    
    if response['statusCode'] != 200:
        raise HTTPException(
            status_code=response['statusCode'],
            detail=json.loads(response['body'])
        )
    
    return json.loads(response['body'])


@app.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task_endpoint(task_id: str):
    """Eliminar una tarea"""
    event = {
        'pathParameters': {'id': task_id},
        'httpMethod': 'DELETE'
    }
    
    response = delete_task_handler.lambda_handler(event, None)
    
    if response['statusCode'] != 200:
        raise HTTPException(
            status_code=response['statusCode'],
            detail=json.loads(response['body'])
        )
    
    return json.loads(response['body'])


@app.post("/tasks/{task_id}/upload")
async def upload_file_endpoint(task_id: str, file: UploadFile = File(...)):
    """Subir archivo a una tarea"""
    
    # Leer contenido del archivo y convertir a base64
    file_content = await file.read()
    file_content_b64 = base64.b64encode(file_content).decode('utf-8')
    
    event = {
        'pathParameters': {'id': task_id},
        'body': json.dumps({
            'file_content': file_content_b64,
            'file_name': file.filename,
            'content_type': file.content_type or 'application/octet-stream'
        }),
        'httpMethod': 'POST'
    }
    
    response = upload_file_handler.lambda_handler(event, None)
    
    if response['statusCode'] != 201:
        raise HTTPException(
            status_code=response['statusCode'],
            detail=json.loads(response['body'])
        )
    
    return json.loads(response['body'])


@app.get("/tasks/stats/summary")
async def get_task_stats():
    """Obtener estadísticas de tareas"""
    try:
        # Obtener todas las tareas
        event = {'queryStringParameters': {'limit': '1000'}}
        response = list_tasks_handler.lambda_handler(event, None)
        
        if response['statusCode'] != 200:
            raise HTTPException(status_code=500, detail="Error obteniendo tareas")
        
        data = json.loads(response['body'])
        tasks = data.get('tasks', [])
        
        # Calcular estadísticas
        stats = {
            'total_tasks': len(tasks),
            'by_status': {},
            'by_priority': {},
            'with_files': 0,
            'overdue': 0
        }
        
        from datetime import datetime
        now = datetime.utcnow()
        
        for task in tasks:
            # Status
            status = task['status']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Priority
            priority = task['priority']
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # Files
            if task.get('files'):
                stats['with_files'] += 1
            
            # Overdue
            if task.get('due_date'):
                try:
                    # Parsear fecha compatible con Python 3.6
                    due_date_str = task['due_date']
                    # Limpiar formato de fecha
                    if due_date_str.endswith('Z'):
                        due_date_str = due_date_str[:-1]
                    elif due_date_str.endswith('+00:00'):
                        due_date_str = due_date_str[:-6]
                    elif '+' in due_date_str:
                        due_date_str = due_date_str.split('+')[0]
                    
                    # Intentar diferentes formatos
                    try:
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M:%S.%f')
                            except ValueError:
                                due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M:%S')
                    
                    if due_date < now and task['status'] != 'completed':
                        stats['overdue'] += 1
                except Exception:
                    # Si no se puede parsear la fecha, continuar sin contar como vencida
                    pass
        
        return {"message": "Estadísticas generadas", "stats": stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando estadísticas: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)