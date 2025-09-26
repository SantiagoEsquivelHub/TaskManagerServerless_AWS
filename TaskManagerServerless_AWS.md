# 🚀 Task Manager Serverless con AWS y Python

Este proyecto es una aplicación **serverless** que gestiona tareas (crear, listar, actualizar, eliminar) usando **APIs REST**, **mensajería** y **servicios de AWS**.  
El objetivo es practicar Lambda, API Gateway, DynamoDB, S3, SQS, SNS, EventBridge, IAM, Secrets Manager, CloudWatch y CDK.

---

## 📌 Arquitectura

1. **API Gateway** → expone endpoints REST.
2. **AWS Lambda** (Python) → maneja la lógica de negocio.
3. **DynamoDB** → almacena las tareas.
4. **S3** → guarda archivos adjuntos a las tareas (ejemplo: CSV con lista de tareas).
5. **SQS** → cola para procesar tareas en segundo plano.
6. **SNS** → notificaciones por correo cuando se crea una tarea.
7. **EventBridge** → dispara un flujo cuando se sube un archivo a S3.
8. **IAM** → roles y políticas con permisos mínimos.
9. **Secrets Manager** → almacenamiento de credenciales (ejemplo: API Key de servicio externo).
10. **CloudWatch** → logs y métricas de Lambdas.
11. **AWS CDK (Python)** → Infraestructura como código para desplegar todo.

---

## 🛠️ Endpoints principales (API REST)

- `POST /tasks` → Crear una tarea  
  - Guarda en **DynamoDB**  
  - Envía evento a **SNS** para notificación  

- `GET /tasks` → Listar tareas  
  - Consulta DynamoDB  

- `PUT /tasks/{id}` → Actualizar tarea  
  - Modifica item en DynamoDB  

- `DELETE /tasks/{id}` → Eliminar tarea  
  - Elimina de DynamoDB  

- `POST /tasks/{id}/upload` → Subir archivo a S3  
  - Guarda en bucket S3 vinculado a la tarea  

---

## 🔄 Flujo de eventos

1. Cuando se crea una tarea:  
   - Lambda guarda en DynamoDB  
   - Publica notificación en **SNS**  
   - Encola mensaje en **SQS** para procesar en background  

2. Cuando se sube un archivo CSV a S3:  
   - **EventBridge** dispara una Lambda  
   - Lambda procesa el archivo y crea tareas en DynamoDB  

---

## 🗂️ Estructura del proyecto

```
task-manager/
│── cdk/                  # Infraestructura (AWS CDK en Python)
│   └── stack.py
│
│── lambdas/              # Código de las funciones Lambda
│   ├── create_task.py
│   ├── list_tasks.py
│   ├── update_task.py
│   ├── delete_task.py
│   ├── upload_file.py
│   ├── process_sqs.py
│   └── process_s3_event.py
│
│── tests/                 # Pruebas con pytest
│   ├── test_create_task.py
│   └── ...
│
│── requirements.txt
│── README.md
```

---

## 🔐 Seguridad

- Cada Lambda tiene un **IAM Role** con permisos mínimos (principio de menor privilegio).
- **Secrets Manager** almacena credenciales sensibles (ejemplo: API Key externa).
- **S3 bucket** con acceso bloqueado al público.
- API Gateway protegido con **API Keys**.

---

## 📊 Observabilidad

- **CloudWatch Logs** para cada Lambda.  
- **CloudWatch Alarms**:  
  - Errores en Lambdas > 5 en 1 minuto.  
  - Cola SQS con mensajes pendientes > 100.  

---

## 🚀 Despliegue

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar AWS CLI con credenciales.

3. Desplegar infraestructura con CDK:
   ```bash
   cdk deploy
   ```

---

## ✅ Próximos pasos

- Integrar **Step Functions** para orquestar flujos más complejos.  
- Añadir monitoreo avanzado con **Grafana/Dynatrace**.  
- Aplicar patrones de diseño GoF (ejemplo: Strategy para validación de tareas).  

---

## 🎯 Aprendizaje clave

Con este proyecto practicarás:  
- Construcción de **APIs REST con Lambda + API Gateway**  
- Persistencia en **DynamoDB y S3**  
- Comunicación asíncrona con **SQS, SNS y EventBridge**  
- Seguridad con **IAM y Secrets Manager**  
- Monitoreo con **CloudWatch**  
- **Infraestructura como Código con CDK**  
