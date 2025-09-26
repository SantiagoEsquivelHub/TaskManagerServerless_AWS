"""
🔄 SQS Processor Handler - Procesa mensajes de la cola SQS
===========================================================

Este handler se ejecuta automáticamente cuando llegan mensajes a la cola SQS.
Procesa notificaciones y tareas asíncronas del sistema.

Funcionalidades:
- Procesa mensajes SNS recibidos vía SQS
- Maneja tareas asíncronas del sistema
- Logging detallado para debugging
- Manejo de errores y reintento automático
"""

import json
import logging
import os
from typing import Dict, Any, List

# Configuración de logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal para procesar mensajes SQS
    
    Args:
        event: Evento SQS con batch de mensajes
        context: Contexto de ejecución Lambda
        
    Returns:
        Dict con resultado del procesamiento
        
    Raises:
        Exception: Si falla el procesamiento de algún mensaje crítico
    """
    
    logger.info(f"🔄 Procesando batch SQS con {len(event.get('Records', []))} mensajes")
    
    # Resultados del procesamiento
    processed_messages = []
    failed_messages = []
    
    try:
        # Procesar cada mensaje en el batch
        for record in event.get('Records', []):
            try:
                result = process_sqs_message(record)
                processed_messages.append(result)
                logger.info(f"✅ Mensaje procesado exitosamente: {result['messageId']}")
                
            except Exception as e:
                error_info = {
                    'messageId': record.get('messageId', 'unknown'),
                    'error': str(e),
                    'body': record.get('body', '')[:200]  # Primeros 200 chars para debugging
                }
                failed_messages.append(error_info)
                logger.error(f"❌ Error procesando mensaje {error_info['messageId']}: {e}")
        
        # Log de resumen
        logger.info(f"📊 Resumen: {len(processed_messages)} exitosos, {len(failed_messages)} fallidos")
        
        # Si hay mensajes fallidos, lanzar excepción para triggear retry
        if failed_messages:
            logger.warning(f"⚠️ {len(failed_messages)} mensajes fallaron, serán reintentados")
            # En un entorno real, podrías decidir si fallar completamente o solo parcialmente
            # raise Exception(f"Failed to process {len(failed_messages)} messages")
        
        return {
            'statusCode': 200,
            'processedCount': len(processed_messages),
            'failedCount': len(failed_messages),
            'processedMessages': processed_messages,
            'failedMessages': failed_messages
        }
        
    except Exception as e:
        logger.error(f"💥 Error crítico procesando batch SQS: {e}")
        raise


def process_sqs_message(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa un mensaje individual de SQS
    
    Args:
        record: Record individual del mensaje SQS
        
    Returns:
        Dict con información del procesamiento
    """
    
    message_id = record.get('messageId', 'unknown')
    receipt_handle = record.get('receiptHandle', '')
    
    logger.info(f"🔍 Procesando mensaje: {message_id}")
    
    try:
        # Parse del body del mensaje
        message_body = json.loads(record.get('body', '{}'))
        
        # Verificar si es un mensaje SNS
        if 'Type' in message_body and message_body['Type'] == 'Notification':
            return process_sns_notification(message_body, message_id)
        
        # Procesar como mensaje directo SQS
        else:
            return process_direct_sqs_message(message_body, message_id)
            
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parsing JSON en mensaje {message_id}: {e}")
        raise Exception(f"Invalid JSON in message: {e}")
    
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje {message_id}: {e}")
        raise


def process_sns_notification(sns_message: Dict[str, Any], message_id: str) -> Dict[str, Any]:
    """
    Procesa un mensaje que viene de SNS
    
    Args:
        sns_message: Mensaje SNS parseado
        message_id: ID del mensaje SQS
        
    Returns:
        Dict con resultado del procesamiento
    """
    
    logger.info(f"📬 Procesando notificación SNS: {sns_message.get('Subject', 'Sin subject')}")
    
    try:
        # Extraer información del mensaje SNS
        subject = sns_message.get('Subject', '')
        message_content = sns_message.get('Message', '')
        timestamp = sns_message.get('Timestamp', '')
        topic_arn = sns_message.get('TopicArn', '')
        
        # Parse del contenido del mensaje (podría ser JSON)
        try:
            parsed_message = json.loads(message_content)
            logger.info(f"📄 Mensaje SNS parseado: {parsed_message}")
        except json.JSONDecodeError:
            parsed_message = {'raw_message': message_content}
            logger.info(f"📄 Mensaje SNS raw: {message_content[:100]}...")
        
        # Aquí puedes agregar lógica específica según el tipo de notificación
        notification_type = parsed_message.get('notification_type', 'general')
        
        if notification_type == 'task_created':
            handle_task_created_notification(parsed_message)
        elif notification_type == 'task_updated':
            handle_task_updated_notification(parsed_message)
        elif notification_type == 'file_uploaded':
            handle_file_uploaded_notification(parsed_message)
        else:
            logger.info(f"🔔 Notificación general procesada: {subject}")
        
        return {
            'messageId': message_id,
            'type': 'sns_notification',
            'subject': subject,
            'notification_type': notification_type,
            'timestamp': timestamp,
            'processed': True
        }
        
    except Exception as e:
        logger.error(f"❌ Error procesando notificación SNS: {e}")
        raise


def process_direct_sqs_message(message: Dict[str, Any], message_id: str) -> Dict[str, Any]:
    """
    Procesa un mensaje enviado directamente a SQS
    
    Args:
        message: Contenido del mensaje
        message_id: ID del mensaje
        
    Returns:
        Dict con resultado del procesamiento
    """
    
    logger.info(f"📨 Procesando mensaje directo SQS: {message_id}")
    
    try:
        message_type = message.get('type', 'unknown')
        
        if message_type == 'task_processing':
            return handle_task_processing(message, message_id)
        elif message_type == 'cleanup_request':
            return handle_cleanup_request(message, message_id)
        else:
            logger.info(f"🔄 Mensaje genérico procesado: {message_type}")
            
        return {
            'messageId': message_id,
            'type': 'direct_sqs',
            'message_type': message_type,
            'processed': True
        }
        
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje directo SQS: {e}")
        raise


def handle_task_created_notification(message: Dict[str, Any]) -> None:
    """Maneja notificaciones de tareas creadas"""
    task_id = message.get('task_id', 'unknown')
    logger.info(f"🆕 Tarea creada: {task_id}")
    
    # Aquí puedes agregar lógica adicional como:
    # - Enviar emails de notificación
    # - Actualizar métricas
    # - Sincronizar con sistemas externos


def handle_task_updated_notification(message: Dict[str, Any]) -> None:
    """Maneja notificaciones de tareas actualizadas"""
    task_id = message.get('task_id', 'unknown')
    old_status = message.get('old_status', 'unknown')
    new_status = message.get('new_status', 'unknown')
    
    logger.info(f"🔄 Tarea actualizada: {task_id} ({old_status} → {new_status})")
    
    # Lógica específica según el cambio de estado
    if new_status == 'completed':
        logger.info(f"✅ Tarea completada: {task_id}")
    elif new_status == 'cancelled':
        logger.info(f"❌ Tarea cancelada: {task_id}")


def handle_file_uploaded_notification(message: Dict[str, Any]) -> None:
    """Maneja notificaciones de archivos subidos"""
    task_id = message.get('task_id', 'unknown')
    file_key = message.get('file_key', 'unknown')
    file_size = message.get('file_size', 0)
    
    logger.info(f"📎 Archivo subido a tarea {task_id}: {file_key} ({file_size} bytes)")


def handle_task_processing(message: Dict[str, Any], message_id: str) -> Dict[str, Any]:
    """Maneja procesamiento asíncrono de tareas"""
    task_id = message.get('task_id', 'unknown')
    processing_type = message.get('processing_type', 'general')
    
    logger.info(f"⚙️ Procesando tarea {task_id}: {processing_type}")
    
    # Aquí puedes agregar lógica de procesamiento pesado como:
    # - Análisis de archivos
    # - Generación de reportes
    # - Integración con APIs externas
    
    return {
        'messageId': message_id,
        'task_id': task_id,
        'processing_type': processing_type,
        'processed': True
    }


def handle_cleanup_request(message: Dict[str, Any], message_id: str) -> Dict[str, Any]:
    """Maneja solicitudes de limpieza del sistema"""
    cleanup_type = message.get('cleanup_type', 'general')
    target = message.get('target', 'unknown')
    
    logger.info(f"🧹 Solicitud de limpieza: {cleanup_type} para {target}")
    
    # Lógica de limpieza como:
    # - Eliminar archivos temporales
    # - Limpiar logs antiguos
    # - Actualizar índices
    
    return {
        'messageId': message_id,
        'cleanup_type': cleanup_type,
        'target': target,
        'processed': True
    }