from typing import Dict, Any
from services.task_service import TaskService
from utils.response_utils import success_response, error_response, get_query_parameters


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler para listar tareas con filtros opcionales
    """
    try:
        # Obtener parámetros de consulta
        query_params = get_query_parameters(event)
        
        # Extraer filtros
        status_filter = query_params.get('status')
        priority_filter = query_params.get('priority')
        tag_filter = query_params.get('tag')
        limit = int(query_params.get('limit', 50))
        
        # Obtener tareas usando el servicio
        task_service = TaskService()
        tasks = task_service.list_tasks(
            status_filter=status_filter,
            priority_filter=priority_filter,
            tag_filter=tag_filter,
            limit=limit
        )
        
        # Respuesta exitosa
        return success_response(
            status_code=200,
            message=f"Se encontraron {len(tasks)} tareas",
            tasks=tasks
        )
        
    except Exception as e:
        return error_response(
            status_code=500,
            message=f'Error al obtener las tareas: {str(e)}'
        )


# Para pruebas locales
if __name__ == "__main__":
    import json
    
    # Evento de prueba - listar todas las tareas
    test_event = {
        'queryStringParameters': {
            'limit': '10'
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
    
    # Evento de prueba - filtrar por status
    test_event_filtered = {
        'queryStringParameters': {
            'status': 'pending',
            'limit': '5'
        }
    }
    
    print("\n--- Con filtro de status ---")
    result = lambda_handler(test_event_filtered, None)
    print(json.dumps(result, indent=2))