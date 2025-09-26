import json
from models import Task
from utils.aws_config import aws_config, get_topic_arn


class NotificationService:
    """Servicio para envío de notificaciones"""
    
    def __init__(self):
        self.sns = aws_config.get_sns_client()
        self.topic_arn = get_topic_arn()
    
    def send_task_created_notification(self, task: Task) -> None:
        """Enviar notificación cuando se crea una tarea"""
        
        if not self.topic_arn:
            print("No se configuró SNS topic ARN")
            return
        
        try:
            message = {
                'task_id': task.id,
                'title': task.title,
                'status': task.status.value,
                'priority': task.priority.value,
                'created_at': task.created_at.isoformat()
            }
            
            self.sns.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                Subject=f'Nueva tarea creada: {task.title}'
            )
            
            print(f"Notificación SNS enviada para tarea {task.id}")
            
        except Exception as e:
            print(f"Error enviando notificación SNS: {str(e)}")
            raise
    
    def send_task_updated_notification(self, task: Task, old_status: str) -> None:
        """Enviar notificación cuando se actualiza una tarea"""
        
        if not self.topic_arn:
            print("No se configuró SNS topic ARN")
            return
        
        try:
            message = {
                'task_id': task.id,
                'title': task.title,
                'old_status': old_status,
                'new_status': task.status.value,
                'priority': task.priority.value,
                'updated_at': task.updated_at.isoformat()
            }
            
            self.sns.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                Subject=f'Tarea actualizada: {task.title}'
            )
            
            print(f"Notificación de actualización SNS enviada para tarea {task.id}")
            
        except Exception as e:
            print(f"Error enviando notificación de actualización SNS: {str(e)}")
            raise
    
    def send_task_deleted_notification(self, task: Task) -> None:
        """Enviar notificación cuando se elimina una tarea"""
        
        if not self.topic_arn:
            print("No se configuró SNS topic ARN")
            return
        
        try:
            message = {
                'task_id': task.id,
                'title': task.title,
                'status': task.status.value,
                'deleted_at': task.updated_at.isoformat()
            }
            
            self.sns.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                Subject=f'Tarea eliminada: {task.title}'
            )
            
            print(f"Notificación de eliminación SNS enviada para tarea {task.id}")
            
        except Exception as e:
            print(f"Error enviando notificación de eliminación SNS: {str(e)}")
            raise