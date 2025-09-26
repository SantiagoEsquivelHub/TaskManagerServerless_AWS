from typing import Dict, Any
from models import TaskUpdate
from services.task_service import TaskService
from utils.response_utils import success_response, error_response, parse_request_body, get_path_parameter


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler para actualizar una tarea existente
    """
    try:
        # Obtener ID de la tarea desde path parameters
        task_id = get_path_parameter(event, 'id')
        if not task_id:
            return error_response(400, 'ID de tarea requerido')
        
        # Parsear el body del request
        body = parse_request_body(event)
        
        # Validar datos de entrada
        task_update = TaskUpdate(**body)
        
        # Actualizar tarea usando el servicio
        task_service = TaskService()
        updated_task = task_service.update_task(task_id, task_update)
        
        if not updated_task:
            return error_response(404, 'Tarea no encontrada')
        
        # Respuesta exitosa
        return success_response(
            status_code=200,
            message="Tarea actualizada exitosamente",
            task=updated_task
        )
        
    except Exception as e:
        return error_response(
            status_code=400,
            message=f'Error al actualizar la tarea: {str(e)}'
        )


# Para pruebas locales
if __name__ == "__main__":
    import json
    
    # Evento de prueba
    test_event = {
        'pathParameters': {
            'id': 'test-task-id'  # Reemplazar con un ID real para pruebas
        },
        'body': json.dumps({
            'title': 'Tarea actualizada',
            'status': 'in_progress',
            'priority': 'high',
            'description': 'Esta tarea ha sido actualizada'
        })
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))