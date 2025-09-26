import uuid
from datetime import datetime
from typing import List, Optional
from models import Task, TaskCreate, TaskUpdate
from repositories.task_repository import TaskRepository
from services.notification_service import NotificationService
from services.queue_service import QueueService


class TaskService:
    """Servicio para lógica de negocio de tareas"""
    
    def __init__(self):
        self.task_repository = TaskRepository()
        self.notification_service = NotificationService()
        self.queue_service = QueueService()
    
    def create_task(self, task_create: TaskCreate) -> Task:
        """Crear una nueva tarea"""
        
        # Generar ID único y timestamps
        task_id = str(uuid.uuid4())
        current_time = datetime.utcnow()
        
        # Crear objeto Task
        task = Task(
            id=task_id,
            title=task_create.title,
            description=task_create.description,
            status=task_create.status,
            priority=task_create.priority,
            due_date=task_create.due_date,
            tags=task_create.tags,
            created_at=current_time,
            updated_at=current_time,
            files=[]
        )
        
        # Guardar en repositorio
        self.task_repository.save(task)
        
        # Procesos asíncronos (no bloquean la respuesta)
        try:
            self.notification_service.send_task_created_notification(task)
            self.queue_service.enqueue_task_processing(task)
        except Exception as e:
            print(f"Error en procesos asíncronos: {str(e)}")
            # No falla la creación si hay problemas con notificaciones
        
        return task
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Obtener tarea por ID"""
        return self.task_repository.find_by_id(task_id)
    
    def list_tasks(self, 
                   status_filter: Optional[str] = None,
                   priority_filter: Optional[str] = None,
                   tag_filter: Optional[str] = None,
                   limit: int = 50) -> List[Task]:
        """Listar tareas con filtros opcionales"""
        
        return self.task_repository.find_all(
            status_filter=status_filter,
            priority_filter=priority_filter,
            tag_filter=tag_filter,
            limit=limit
        )
    
    def update_task(self, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """Actualizar una tarea existente"""
        
        # Verificar que la tarea existe
        existing_task = self.task_repository.find_by_id(task_id)
        if not existing_task:
            return None
        
        # Preparar campos para actualizar
        updates = {}
        
        if task_update.title is not None:
            updates['title'] = task_update.title
        if task_update.description is not None:
            updates['description'] = task_update.description
        if task_update.status is not None:
            updates['status'] = task_update.status
        if task_update.priority is not None:
            updates['priority'] = task_update.priority
        if task_update.due_date is not None:
            updates['due_date'] = task_update.due_date
        if task_update.tags is not None:
            updates['tags'] = task_update.tags
        
        # Actualizar en repositorio
        updated_task = self.task_repository.update(task_id, updates)
        
        return updated_task
    
    def delete_task(self, task_id: str) -> Optional[Task]:
        """Eliminar una tarea"""
        
        # Verificar que la tarea existe
        existing_task = self.task_repository.find_by_id(task_id)
        if not existing_task:
            return None
        
        # Eliminar archivos asociados (si existen)
        if existing_task.files:
            try:
                from services.file_service import FileService
                file_service = FileService()
                file_service.delete_files(existing_task.files)
            except Exception as e:
                print(f"Error eliminando archivos: {str(e)}")
                # No falla la eliminación si hay problemas con archivos
        
        # Eliminar de repositorio
        self.task_repository.delete(task_id)
        
        return existing_task
    
    def add_file_to_task(self, task_id: str, file_key: str) -> Optional[Task]:
        """Agregar archivo a una tarea"""
        
        # Verificar que la tarea exists
        existing_task = self.task_repository.find_by_id(task_id)
        if not existing_task:
            return None
        
        # Agregar archivo a la tarea
        self.task_repository.add_file_to_task(task_id, file_key)
        
        # Retornar tarea actualizada
        return self.task_repository.find_by_id(task_id)