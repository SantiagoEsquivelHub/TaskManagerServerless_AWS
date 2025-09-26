import json
from typing import Dict, Any, Optional
from models import TaskResponse, Task
from datetime import datetime


def success_response(status_code: int, message: str, task: Optional[Task] = None, tasks: Optional[list] = None) -> Dict[str, Any]:
    """Crear respuesta exitosa estándar"""
    response = TaskResponse(
        message=message,
        task=task,
        tasks=tasks
    )
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response.dict(), default=str)
    }


def error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Crear respuesta de error estándar"""
    error_body = {
        'message': message
    }
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(error_body)
    }


def parse_request_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parsear el body del request HTTP"""
    if isinstance(event.get('body'), str):
        return json.loads(event['body'])
    else:
        return event.get('body', {})


def get_path_parameter(event: Dict[str, Any], param_name: str) -> Optional[str]:
    """Obtener parámetro de path"""
    path_params = event.get('pathParameters') or {}
    return path_params.get(param_name)


def get_query_parameters(event: Dict[str, Any]) -> Dict[str, str]:
    """Obtener parámetros de query string"""
    return event.get('queryStringParameters') or {}