import json
from models import Task
from utils.aws_config import aws_config, get_queue_url


class QueueService:
    """Servicio para manejo de colas SQS"""
    
    def __init__(self):
        self.sqs = aws_config.get_sqs_client()
        self.queue_url = get_queue_url()
    
    def enqueue_task_processing(self, task: Task) -> None:
        """Encolar tarea para procesamiento en background"""
        
        if not self.queue_url:
            print("No se configuró SQS queue URL")
            return
        
        try:
            message = {
                'action': 'process_new_task',
                'task_id': task.id,
                'task_data': task.dict()
            }
            
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message, default=str)
            )
            
            print(f"Mensaje enviado a SQS para tarea {task.id}")
            
        except Exception as e:
            print(f"Error enviando mensaje a SQS: {str(e)}")
            raise
    
    def enqueue_task_reminder(self, task_id: str) -> None:
        """Encolar recordatorio de tarea"""
        
        if not self.queue_url:
            print("No se configuró SQS queue URL")
            return
        
        try:
            message = {
                'action': 'send_reminder',
                'task_id': task_id
            }
            
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message, default=str)
            )
            
            print(f"Recordatorio encolado para tarea {task_id}")
            
        except Exception as e:
            print(f"Error encolando recordatorio: {str(e)}")
            raise
    
    def enqueue_cleanup_tasks(self, days_old: int = 30) -> None:
        """Encolar limpieza de tareas completadas"""
        
        if not self.queue_url:
            print("No se configuró SQS queue URL")
            return
        
        try:
            message = {
                'action': 'cleanup_completed_tasks',
                'days_old': days_old
            }
            
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message, default=str)
            )
            
            print(f"Limpieza de tareas encolada (>{days_old} días)")
            
        except Exception as e:
            print(f"Error encolando limpieza: {str(e)}")
            raise
    
    def enqueue_generate_report(self, report_type: str = 'summary') -> None:
        """Encolar generación de reporte"""
        
        if not self.queue_url:
            print("No se configuró SQS queue URL")
            return
        
        try:
            message = {
                'action': 'generate_task_report',
                'report_type': report_type
            }
            
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message, default=str)
            )
            
            print(f"Generación de reporte {report_type} encolada")
            
        except Exception as e:
            print(f"Error encolando reporte: {str(e)}")
            raise