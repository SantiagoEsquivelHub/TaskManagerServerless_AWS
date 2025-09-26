#!/usr/bin/env python3
"""
📊 DASHBOARD EN TIEMPO REAL - SNS & SQS
======================================

Monitor visual para ver notificaciones SNS y mensajes SQS en tiempo real.
"""

import boto3
import json
import time
import os
from datetime import datetime
from collections import defaultdict

# Configuración LocalStack
LOCALSTACK_ENDPOINT = 'http://localhost:4566'

def get_localstack_clients():
    """Configurar clientes AWS para LocalStack"""
    return (
        boto3.client('sns', endpoint_url=LOCALSTACK_ENDPOINT, region_name='us-east-1', 
                    aws_access_key_id='test', aws_secret_access_key='test'),
        boto3.client('sqs', endpoint_url=LOCALSTACK_ENDPOINT, region_name='us-east-1',
                    aws_access_key_id='test', aws_secret_access_key='test')
    )

def clear_screen():
    """Limpiar pantalla"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_queue_stats():
    """Obtener estadísticas de colas SQS"""
    try:
        _, sqs = get_localstack_clients()
        
        queues = sqs.list_queues().get('QueueUrls', [])
        stats = {}
        
        for queue_url in queues:
            queue_name = queue_url.split('/')[-1]
            
            attrs = sqs.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesNotVisible']
            )
            
            stats[queue_name] = {
                'url': queue_url,
                'available': int(attrs['Attributes'].get('ApproximateNumberOfMessages', 0)),
                'in_flight': int(attrs['Attributes'].get('ApproximateNumberOfMessagesNotVisible', 0))
            }
        
        return stats
    except Exception as e:
        return {"error": str(e)}

def get_sns_stats():
    """Obtener estadísticas de tópicos SNS"""
    try:
        sns, _ = get_localstack_clients()
        
        topics = sns.list_topics().get('Topics', [])
        stats = {}
        
        for topic in topics:
            topic_arn = topic['TopicArn']
            topic_name = topic_arn.split(':')[-1]
            
            # Obtener suscriptores
            subs = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
            subscriber_count = len(subs.get('Subscriptions', []))
            
            stats[topic_name] = {
                'arn': topic_arn,
                'subscribers': subscriber_count
            }
        
        return stats
    except Exception as e:
        return {"error": str(e)}

def read_recent_messages(limit=5):
    """Leer mensajes recientes de SQS"""
    try:
        _, sqs = get_localstack_clients()
        
        queues = sqs.list_queues().get('QueueUrls', [])
        if not queues:
            return []
        
        # Usar la primera cola
        queue_url = queues[0]
        
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=limit,
            WaitTimeSeconds=1
        )
        
        messages = response.get('Messages', [])
        parsed_messages = []
        
        for msg in messages:
            try:
                body = json.loads(msg['Body'])
                parsed_messages.append({
                    'id': msg['MessageId'][:8],
                    'action': body.get('action', 'unknown'),
                    'task_id': body.get('task_id', 'N/A')[:8],
                    'title': body.get('task_data', {}).get('title', 'N/A'),
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            except:
                parsed_messages.append({
                    'id': msg['MessageId'][:8],
                    'action': 'parse_error',
                    'task_id': 'N/A',
                    'title': msg['Body'][:50],
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        
        return parsed_messages
    except Exception as e:
        return [{"error": str(e)}]

def display_dashboard():
    """Mostrar dashboard en tiempo real"""
    print("🔄 Iniciando dashboard en tiempo real...")
    print("   Presiona Ctrl+C para salir")
    time.sleep(2)
    
    try:
        while True:
            clear_screen()
            
            # Header
            print("📊 DASHBOARD SNS/SQS EN TIEMPO REAL")
            print("=" * 60)
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            # SNS Stats
            print("\n🔔 TÓPICOS SNS:")
            sns_stats = get_sns_stats()
            if 'error' in sns_stats:
                print(f"❌ Error: {sns_stats['error']}")
            else:
                for name, info in sns_stats.items():
                    print(f"   📍 {name}")
                    print(f"      └─ Suscriptores: {info['subscribers']}")
            
            # SQS Stats
            print("\n📦 COLAS SQS:")
            queue_stats = get_queue_stats()
            if 'error' in queue_stats:
                print(f"❌ Error: {queue_stats['error']}")
            else:
                for name, info in queue_stats.items():
                    print(f"   📍 {name}")
                    print(f"      └─ Mensajes disponibles: {info['available']}")
                    print(f"      └─ En procesamiento: {info['in_flight']}")
            
            # Recent Messages
            print("\n📬 MENSAJES RECIENTES:")
            recent_messages = read_recent_messages(5)
            if not recent_messages:
                print("   📭 No hay mensajes recientes")
            elif 'error' in recent_messages[0]:
                print(f"   ❌ Error: {recent_messages[0]['error']}")
            else:
                for msg in recent_messages:
                    print(f"   📨 {msg['timestamp']} | {msg['action']} | Task: {msg['task_id']} | {msg['title'][:30]}")
            
            # Instructions
            print("\n" + "=" * 60)
            print("💡 PARA PROBAR:")
            print("   • Crear tarea: POST http://localhost:8000/tasks")
            print("   • Ver Swagger: http://localhost:8000/docs")
            print("   • Presiona Ctrl+C para salir")
            
            # Refresh every 3 seconds
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard cerrado")

def show_localstack_commands():
    """Mostrar comandos útiles de LocalStack"""
    print("🛠️ COMANDOS ÚTILES PARA VERIFICAR SNS/SQS:")
    print("=" * 60)
    
    print("\n📋 LOCALSTACK WEB UI:")
    print("   🌐 http://localhost:4566/_localstack/health")
    print("   🖥️  LocalStack Dashboard: https://app.localstack.cloud")
    
    print("\n🔔 VERIFICAR SNS (usando boto3):")
    print("   python -c \"")
    print("   import boto3")
    print("   sns = boto3.client('sns', endpoint_url='http://localhost:4566', region_name='us-east-1', aws_access_key_id='test', aws_secret_access_key='test')")
    print("   print(sns.list_topics())")
    print("   \"")
    
    print("\n📦 VERIFICAR SQS (usando boto3):")
    print("   python -c \"")
    print("   import boto3")
    print("   sqs = boto3.client('sqs', endpoint_url='http://localhost:4566', region_name='us-east-1', aws_access_key_id='test', aws_secret_access_key='test')")
    print("   print(sqs.list_queues())")
    print("   \"")
    
    print("\n🧪 CREAR TAREA DE PRUEBA:")
    print("   curl -X POST http://localhost:8000/tasks \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"title\":\"Prueba notificaciones\",\"priority\":\"high\"}'")
    
    print("\n📊 ESTE SCRIPT:")
    print("   python sns_sqs_dashboard.py           # Dashboard en tiempo real")
    print("   python sns_sqs_dashboard.py help     # Ver esta ayuda")

def main():
    """Función principal"""
    if len(os.sys.argv) > 1 and os.sys.argv[1] == 'help':
        show_localstack_commands()
    else:
        display_dashboard()

if __name__ == "__main__":
    main()