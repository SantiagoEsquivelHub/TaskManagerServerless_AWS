from typing import List, Optional, Dict, Any
from datetime import datetime
from models import Task, TaskStatus, TaskPriority
from utils.aws_config import aws_config, get_table_name


class TaskRepository:
    """Repository para operaciones de DynamoDB con tareas"""
    
    def __init__(self):
        self.dynamodb = aws_config.get_dynamodb_resource()
        self.table = self.dynamodb.Table(get_table_name())
    
    def save(self, task: Task) -> None:
        """Guardar tarea en DynamoDB"""
        item = self._task_to_dynamodb_item(task)
        # Remover campos None
        item = {k: v for k, v in item.items() if v is not None}
        self.table.put_item(Item=item)
    
    def find_by_id(self, task_id: str) -> Optional[Task]:
        """Buscar tarea por ID"""
        try:
            response = self.table.get_item(Key={'id': task_id})
            item = response.get('Item')
            
            if not item:
                return None
            
            return self._dynamodb_item_to_task(item)
            
        except Exception as e:
            print(f"Error obteniendo tarea {task_id}: {str(e)}")
            return None
    
    def find_all(self, 
                 status_filter: Optional[str] = None,
                 priority_filter: Optional[str] = None,
                 tag_filter: Optional[str] = None,
                 limit: int = 50) -> List[Task]:
        """Buscar tareas con filtros opcionales"""
        
        # Construir parámetros de scan
        scan_params = {'Limit': limit}
        
        # Aplicar filtros si están presentes
        filter_expressions = []
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        if status_filter:
            filter_expressions.append('#status = :status')
            expression_attribute_names['#status'] = 'status'
            expression_attribute_values[':status'] = status_filter
        
        if priority_filter:
            filter_expressions.append('priority = :priority')
            expression_attribute_values[':priority'] = priority_filter
        
        if tag_filter:
            filter_expressions.append('contains(tags, :tag)')
            expression_attribute_values[':tag'] = tag_filter
        
        # Agregar filtros a los parámetros si existen
        if filter_expressions:
            scan_params['FilterExpression'] = ' AND '.join(filter_expressions)
            scan_params['ExpressionAttributeValues'] = expression_attribute_values
            
            if expression_attribute_names:
                scan_params['ExpressionAttributeNames'] = expression_attribute_names
        
        # Ejecutar scan
        response = self.table.scan(**scan_params)
        items = response.get('Items', [])
        
        # Convertir items de DynamoDB a modelos Task
        tasks = []
        for item in items:
            try:
                task = self._dynamodb_item_to_task(item)
                tasks.append(task)
            except Exception as e:
                print(f"Error convirtiendo item: {item}, error: {str(e)}")
                continue
        
        # Ordenar por fecha de creación (más recientes primero)
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        return tasks
    
    def update(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """Actualizar tarea en DynamoDB"""
        
        # Construir expresión de actualización
        update_expressions = []
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        # Siempre actualizar el timestamp
        update_expressions.append('#updated_at = :updated_at')
        expression_attribute_names['#updated_at'] = 'updated_at'
        expression_attribute_values[':updated_at'] = datetime.utcnow().isoformat()
        
        # Actualizar campos proporcionados
        for field, value in updates.items():
            if value is not None:
                if field == 'status':
                    update_expressions.append('#status = :status')
                    expression_attribute_names['#status'] = 'status'
                    expression_attribute_values[':status'] = value.value if hasattr(value, 'value') else value
                elif field == 'title':
                    update_expressions.append('#title = :title')
                    expression_attribute_names['#title'] = 'title'
                    expression_attribute_values[':title'] = value
                elif field == 'due_date':
                    update_expressions.append('due_date = :due_date')
                    expression_attribute_values[':due_date'] = value.isoformat() if hasattr(value, 'isoformat') else value
                else:
                    update_expressions.append(f'{field} = :{field}')
                    if hasattr(value, 'value'):  # Enum
                        expression_attribute_values[f':{field}'] = value.value
                    else:
                        expression_attribute_values[f':{field}'] = value
        
        # Ejecutar actualización
        update_expression = 'SET ' + ', '.join(update_expressions)
        
        response = self.table.update_item(
            Key={'id': task_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues='ALL_NEW'
        )
        
        # Convertir respuesta a modelo Task
        updated_item = response['Attributes']
        return self._dynamodb_item_to_task(updated_item)
    
    def delete(self, task_id: str) -> None:
        """Eliminar tarea de DynamoDB"""
        self.table.delete_item(Key={'id': task_id})
    
    def add_file_to_task(self, task_id: str, file_key: str) -> None:
        """Agregar archivo a la lista de archivos de la tarea"""
        self.table.update_item(
            Key={'id': task_id},
            UpdateExpression='SET files = list_append(if_not_exists(files, :empty_list), :new_file)',
            ExpressionAttributeValues={
                ':new_file': [file_key],
                ':empty_list': []
            }
        )
    
    def _task_to_dynamodb_item(self, task: Task) -> Dict[str, Any]:
        """Convertir modelo Task a item de DynamoDB"""
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status.value,
            'priority': task.priority.value,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'tags': task.tags,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat(),
            'files': task.files
        }
    
    def _dynamodb_item_to_task(self, item: Dict[str, Any]) -> Task:
        """Convertir item de DynamoDB a modelo Task"""
        
        # Manejar fechas - compatible con Python 3.6
        def parse_datetime(date_str):
            """Parsear fecha ISO compatible con Python 3.6"""
            if not date_str:
                return None
            # Eliminar timezone info si está presente para simplificar
            if date_str.endswith('+00:00'):
                date_str = date_str[:-6]
            elif 'T' in date_str and '+' in date_str:
                date_str = date_str.split('+')[0]
            elif 'T' in date_str and 'Z' in date_str:
                date_str = date_str.replace('Z', '')
            
            try:
                return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    # Fallback para otros formatos
                    return datetime.now()
        
        created_at = parse_datetime(item['created_at'])
        updated_at = parse_datetime(item['updated_at'])
        due_date = None
        if item.get('due_date'):
            due_date = parse_datetime(item['due_date'])
        
        return Task(
            id=item['id'],
            title=item['title'],
            description=item.get('description'),
            status=TaskStatus(item['status']),
            priority=TaskPriority(item['priority']),
            due_date=due_date,
            tags=item.get('tags', []),
            created_at=created_at,
            updated_at=updated_at,
            files=item.get('files', [])
        )