from typing import Dict, Any
from models import TaskCreate
from services.task_service import TaskService
from utils.response_utils import success_response, error_response, parse_request_body


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler para crear una nueva tarea
    """
    try:
        # Parsear el body del request
        body = parse_request_body(event)
        
        # Validar datos de entrada
        task_create = TaskCreate(**body)
        
        # Crear tarea usando el servicio
        task_service = TaskService()
        task = task_service.create_task(task_create)
        
        # Respuesta exitosa
        return success_response(
            status_code=201,
            message="Tarea creada exitosamente",
            task=task
        )
        
    except Exception as e:
        return error_response(
            status_code=400,
            message=f'Error al crear la tarea: {str(e)}'
        )


# Para pruebas locales
if __name__ == "__main__":
    import json
    
    # Evento de prueba
    test_event = {
        'body': json.dumps({
            'title': 'Mi primera tarea',
            'description': 'Esta es una tarea de prueba',
            'priority': 'high',
            'tags': ['trabajo', 'urgente']
        })
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))