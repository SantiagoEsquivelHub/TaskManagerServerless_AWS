from typing import Dict, Any
from services.task_service import TaskService
from utils.response_utils import success_response, error_response, get_path_parameter


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler para eliminar una tarea
    """
    try:
        # Obtener ID de la tarea desde path parameters
        task_id = get_path_parameter(event, 'id')
        if not task_id:
            return error_response(400, 'ID de tarea requerido')
        
        # Eliminar tarea usando el servicio
        task_service = TaskService()
        deleted_task = task_service.delete_task(task_id)
        
        if not deleted_task:
            return error_response(404, 'Tarea no encontrada')
        
        # Respuesta exitosa
        return success_response(
            status_code=200,
            message=f"Tarea '{deleted_task.title}' eliminada exitosamente"
        )
        
    except Exception as e:
        return error_response(
            status_code=400,
            message=f'Error al eliminar la tarea: {str(e)}'
        )


# Para pruebas locales
if __name__ == "__main__":
    import json
    
    # Evento de prueba
    test_event = {
        'pathParameters': {
            'id': 'test-task-id'  # Reemplazar con un ID real para pruebas
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))