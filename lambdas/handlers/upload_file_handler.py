import json
from typing import Dict, Any
from models import FileUploadResponse  
from services.task_service import TaskService
from services.file_service import FileService
from utils.response_utils import success_response, error_response, parse_request_body, get_path_parameter


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler para subir archivos a S3 y vincularlos a una tarea
    """
    try:
        # Obtener ID de la tarea desde path parameters
        task_id = get_path_parameter(event, 'id')
        if not task_id:
            return error_response(400, 'ID de tarea requerido')
        
        # Verificar si la tarea existe
        task_service = TaskService()
        existing_task = task_service.get_task_by_id(task_id)
        if not existing_task:
            return error_response(404, 'Tarea no encontrada')
        
        # Parsear el body del request
        body = parse_request_body(event)
        
        # Obtener datos del archivo
        file_content = body.get('file_content')  # Base64 encoded
        file_name = body.get('file_name')
        content_type = body.get('content_type', 'application/octet-stream')
        
        if not file_content or not file_name:
            return error_response(400, 'Contenido del archivo y nombre son requeridos')
        
        # Subir archivo usando el servicio
        file_service = FileService()
        s3_key = file_service.upload_file(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type,
            task_id=task_id
        )
        
        # Actualizar la tarea con la referencia del archivo
        task_service.add_file_to_task(task_id, s3_key)
        
        # Generar URL del archivo
        file_url = file_service.generate_file_url(s3_key)
        
        # Respuesta exitosa
        response_data = {
            'message': 'Archivo subido exitosamente',
            'file_url': file_url,
            'task_id': task_id,
            's3_key': s3_key
        }
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        return error_response(
            status_code=400,
            message=f'Error al subir el archivo: {str(e)}'
        )


# Para pruebas locales
if __name__ == "__main__":
    import json
    import base64
    
    # Ejemplo de archivo pequeño en base64 (texto "Hello World!")
    test_file_content = base64.b64encode(b"Hello World! This is a test file.").decode('utf-8')
    
    test_event = {
        'pathParameters': {
            'id': 'test-task-id'  # Reemplazar con un ID real para pruebas
        },
        'body': json.dumps({
            'file_content': test_file_content,
            'file_name': 'test_file.txt',
            'content_type': 'text/plain'
        })
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))