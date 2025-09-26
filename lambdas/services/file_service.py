import uuid
import base64
from typing import List
from utils.aws_config import aws_config, get_bucket_name


class FileService:
    """Servicio para manejo de archivos en S3"""
    
    def __init__(self):
        self.s3 = aws_config.get_s3_client()
        self.bucket_name = get_bucket_name()
    
    def upload_file(self, file_content: str, file_name: str, content_type: str, task_id: str) -> str:
        """Subir archivo a S3 y retornar la key"""
        
        # Decodificar contenido base64
        try:
            file_data = base64.b64decode(file_content)
        except Exception as e:
            raise ValueError(f"Error decodificando archivo base64: {str(e)}")
        
        # Generar key única para el archivo
        file_extension = file_name.split('.')[-1] if '.' in file_name else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        s3_key = f"tasks/{task_id}/files/{unique_filename}"
        
        # Subir archivo a S3
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=file_data,
            ContentType=content_type,
            Metadata={
                'original_filename': file_name,
                'task_id': task_id,
                'uploaded_by': 'task-manager-api'
            }
        )
        
        print(f"Archivo subido a S3: {s3_key}")
        return s3_key
    
    def delete_files(self, file_keys: List[str]) -> None:
        """Eliminar archivos de S3"""
        if not file_keys:
            return
        
        try:
            # Preparar lista de objetos para eliminar
            objects_to_delete = [{'Key': key} for key in file_keys]
            
            # Eliminar objetos en lote
            response = self.s3.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    'Objects': objects_to_delete,
                    'Quiet': True
                }
            )
            
            print(f"Eliminados {len(file_keys)} archivos de S3: {file_keys}")
            
            # Verificar si hubo errores
            if 'Errors' in response and response['Errors']:
                for error in response['Errors']:
                    print(f"Error eliminando {error['Key']}: {error['Message']}")
            
        except Exception as e:
            print(f"Error eliminando archivos de S3: {str(e)}")
            raise
    
    def generate_file_url(self, s3_key: str) -> str:
        """Generar URL para acceder al archivo"""
        
        if aws_config.use_localstack:
            # Para LocalStack, generar URL local
            return f"{aws_config.localstack_endpoint}/{self.bucket_name}/{s3_key}"
        else:
            # Para AWS real, generar presigned URL
            try:
                url = self.s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': s3_key},
                    ExpiresIn=3600  # 1 hora
                )
                return url
            except Exception as e:
                print(f"Error generando presigned URL: {str(e)}")
                return f"s3://{self.bucket_name}/{s3_key}"
    
    def get_file_metadata(self, s3_key: str) -> dict:
        """Obtener metadatos de un archivo"""
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=s3_key)
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response['ContentType'],
                'metadata': response.get('Metadata', {})
            }
        except Exception as e:
            print(f"Error obteniendo metadatos de {s3_key}: {str(e)}")
            return {}
    
    def list_task_files(self, task_id: str) -> List[dict]:
        """Listar archivos de una tarea específica"""
        try:
            prefix = f"tasks/{task_id}/files/"
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'url': self.generate_file_url(obj['Key'])
                })
            
            return files
            
        except Exception as e:
            print(f"Error listando archivos de tarea {task_id}: {str(e)}")
            return []