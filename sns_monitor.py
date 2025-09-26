#!/usr/bin/env python3
"""
📧 SUSCRIPTOR DE NOTIFICACIONES SNS
==================================

Script para suscribirse al tópico SNS y ver las notificaciones en tiempo real.
"""

import boto3
import json
import time
import sys
import threading
from datetime import datetime

# Configuración LocalStack
LOCALSTACK_ENDPOINT = 'http://localhost:4566'
TOPIC_ARN = 'arn:aws:sns:us-east-1:000000000000:task-notifications'

def get_clients():
    """Obtener clientes AWS configurados para LocalStack"""
    config = {
        'endpoint_url': LOCALSTACK_ENDPOINT,
        'region_name': 'us-east-1',
        'aws_access_key_id': 'test',
        'aws_secret_access_key': 'test'
    }
    
    return (
        boto3.client('sns', **config),
        boto3.client('sqs', **config)
    )

def create_notification_queue():
    """Crear cola temporal para recibir notificaciones SNS"""
    print("📦 Creando cola temporal para notificaciones...")
    
    sns, sqs = get_clients()
    
    # Crear cola temporal
    queue_name = f'sns-notifications-{int(time.time())}'
    queue_response = sqs.create_queue(QueueName=queue_name)
    queue_url = queue_response['QueueUrl']
    
    print(f"   ✅ Cola creada: {queue_name}")
    print(f"   🔗 URL: {queue_url}")
    
    # Obtener ARN de la cola
    queue_attributes = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['QueueArn']
    )
    queue_arn = queue_attributes['Attributes']['QueueArn']
    
    # Suscribir la cola al tópico SNS
    print(f"🔗 Suscribiendo cola al tópico SNS...")
    subscription_response = sns.subscribe(
        TopicArn=TOPIC_ARN,
        Protocol='sqs',
        Endpoint=queue_arn
    )
    
    subscription_arn = subscription_response['SubscriptionArn']
    print(f"   ✅ Suscripción creada: {subscription_arn}")
    
    return queue_url, subscription_arn

def listen_for_notifications(queue_url):
    """Escuchar notificaciones en tiempo real"""
    print(f"\n👂 ESCUCHANDO NOTIFICACIONES EN TIEMPO REAL...")
    print("=" * 60)
    print("💡 Crea tareas usando: http://localhost:8000/docs")
    print("⏹️  Presiona Ctrl+C para detener")
    print("-" * 60)
    
    _, sqs = get_clients()
    
    try:
        while True:
            # Recibir mensajes
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=5,  # Long polling
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            
            for message in messages:
                try:
                    # Parsear el mensaje SNS
                    body = json.loads(message['Body'])
                    
                    # Extraer información de la notificación
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    message_text = body.get('Message', '')
                    subject = body.get('Subject', 'Sin asunto')
                    
                    print(f"\n🔔 [{timestamp}] {subject}")
                    
                    # Intentar parsear el mensaje como JSON
                    try:
                        message_data = json.loads(message_text)
                        print(f"   📝 Tarea ID: {message_data.get('task_id', 'N/A')}")
                        print(f"   📋 Título: {message_data.get('title', 'N/A')}")
                        print(f"   📊 Estado: {message_data.get('status', 'N/A')}")
                        print(f"   ⚡ Prioridad: {message_data.get('priority', 'N/A')}")
                        
                        if 'old_status' in message_data:
                            print(f"   🔄 Cambio: {message_data['old_status']} → {message_data['new_status']}")
                        
                        if 'created_at' in message_data:
                            print(f"   📅 Creado: {message_data['created_at']}")
                        
                    except json.JSONDecodeError:
                        print(f"   📄 Mensaje: {message_text}")
                    
                    print("   " + "-" * 50)
                    
                    # Eliminar mensaje de la cola
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    
                except Exception as e:
                    print(f"   ❌ Error procesando mensaje: {str(e)}")
            
            if not messages:
                # Mostrar punto para indicar que está escuchando
                print(".", end="", flush=True)
    
    except KeyboardInterrupt:
        print(f"\n\n👋 Deteniendo monitor de notificaciones...")

def cleanup_resources(queue_url, subscription_arn):
    """Limpiar recursos temporales"""
    print(f"\n🧹 Limpiando recursos temporales...")
    
    sns, sqs = get_clients()
    
    try:
        # Cancelar suscripción
        sns.unsubscribe(SubscriptionArn=subscription_arn)
        print(f"   ✅ Suscripción cancelada")
        
        # Eliminar cola
        sqs.delete_queue(QueueUrl=queue_url)
        print(f"   ✅ Cola eliminada")
        
    except Exception as e:
        print(f"   ⚠️ Error limpiando recursos: {str(e)}")

def test_send_notification():
    """Enviar notificación de prueba"""
    print("🧪 ENVIANDO NOTIFICACIÓN DE PRUEBA...")
    
    sns, _ = get_clients()
    
    test_message = {
        'task_id': 'test-123',
        'title': 'Notificación de prueba',
        'status': 'pending',
        'priority': 'high',
        'created_at': datetime.now().isoformat()
    }
    
    try:
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(test_message),
            Subject='🧪 Prueba de notificación manual'
        )
        print("   ✅ Notificación de prueba enviada")
    except Exception as e:
        print(f"   ❌ Error enviando notificación: {str(e)}")

def show_instructions():
    """Mostrar instrucciones de uso"""
    print("📧 MONITOR DE NOTIFICACIONES SNS")
    print("=" * 60)
    print()
    print("Este script te permite ver las notificaciones SNS en tiempo real.")
    print()
    print("🔧 COMANDOS:")
    print("   python sns_monitor.py              # Monitor en tiempo real")
    print("   python sns_monitor.py test         # Enviar notificación de prueba")
    print("   python sns_monitor.py help         # Ver esta ayuda")
    print()
    print("💡 CÓMO FUNCIONA:")
    print("   1. Crea una cola SQS temporal")
    print("   2. Suscribe la cola al tópico SNS")
    print("   3. Escucha mensajes en tiempo real")
    print("   4. Muestra las notificaciones formateadas")
    print("   5. Limpia recursos al salir")
    print()
    print("🧪 PARA PROBAR:")
    print("   • Abre http://localhost:8000/docs")
    print("   • Crea, actualiza o elimina tareas")
    print("   • Ve las notificaciones aquí en tiempo real")

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            test_send_notification()
            return
        elif command == 'help':
            show_instructions()
            return
    
    # Monitor en tiempo real
    print("🚀 INICIANDO MONITOR DE NOTIFICACIONES SNS...")
    
    try:
        # Crear cola y suscripción
        queue_url, subscription_arn = create_notification_queue()
        
        # Enviar notificación de prueba para verificar
        print("\n🧪 Enviando notificación de prueba...")
        test_send_notification()
        
        # Esperar un momento para que llegue la notificación
        time.sleep(2)
        
        # Escuchar notificaciones
        listen_for_notifications(queue_url)
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        # Limpiar recursos
        try:
            cleanup_resources(queue_url, subscription_arn)
        except:
            pass

if __name__ == "__main__":
    main()