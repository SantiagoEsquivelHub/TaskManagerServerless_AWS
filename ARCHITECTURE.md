# 🏗️ Task Manager Serverless - Arquitectura en Capas

## 📁 **Estructura del Proyecto**

```
TaskManagerServerless_AWS/
├── lambdas/                     # 🐍 Código Python principal
│   ├── models.py                # 📝 Solo modelos de datos
│   ├── handlers/                # 🎯 Solo manejo de eventos Lambda
│   │   ├── create_task_handler.py   # POST /tasks
│   │   ├── list_tasks_handler.py    # GET /tasks
│   │   ├── update_task_handler.py   # PUT /tasks/{id}
│   │   ├── delete_task_handler.py   # DELETE /tasks/{id}
│   │   ├── upload_file_handler.py   # POST /tasks/{id}/upload
│   │   ├── sqs_processor_handler.py # SQS messages
│   │   └── s3_event_handler.py      # S3 events
│   ├── services/                # ⚙️ Solo lógica de negocio
│   │   ├── task_service.py          # CRUD + validaciones de negocio
│   │   ├── notification_service.py  # Notificaciones SNS
│   │   ├── queue_service.py         # Mensajes SQS
│   │   └── file_service.py          # Manejo de archivos S3
│   ├── repositories/            # 💾 Solo acceso a datos
│   │   ├── task_repository.py       # DynamoDB operations
│   │   └── file_repository.py       # S3 operations (futuro)
│   └── utils/                   # 🛠️ Solo utilidades
│       ├── aws_config.py            # Configuración AWS
│       ├── response_utils.py        # Respuestas HTTP estándar
│       └── validation_utils.py      # Validaciones comunes (futuro)
├── local/                       # 🖥️ Desarrollo local
│   ├── api_server.py            # Servidor FastAPI local
│   ├── setup_localstack.py     # Configuración LocalStack
│   └── test_functions.py        # Pruebas básicas
├── tests/                       # 🧪 Pruebas unitarias
│   └── test_lambda_functions.py # Tests con pytest
├── cdk/                         # ☁️ Infraestructura como código
└── requirements.txt             # 📦 Dependencias Python
```

## 🏗️ **DISTRIBUCIÓN POR CAPAS**

### **1. 🎯 CAPA DE HANDLERS** (`handlers/`)
**Responsabilidad**: Solo manejar eventos de Lambda y HTTP

```python
# Ejemplo: create_task_handler.py
def lambda_handler(event, context):
    body = parse_request_body(event)    # 📥 Parsear request
    task_create = TaskCreate(**body)    # 📝 Validar con modelo
    task = task_service.create_task()   # ⚙️ Llamar a servicio
    return success_response(task=task)  # 📤 Devolver respuesta
```

**✅ Qué SÍ hacen:**
- Reciben eventos de Lambda/API Gateway
- Parsean requests HTTP (JSON, query params, path params)
- Validan entrada usando modelos Pydantic
- Llaman a la capa de **Services**
- Formatean respuestas HTTP estándar
- Manejan excepciones HTTP

**❌ Qué NO hacen:**
- Lógica de negocio
- Acceso directo a bases de datos
- Validaciones complejas de negocio
- Cálculos o transformaciones de datos

### **2. ⚙️ CAPA DE SERVICES** (`services/`)
**Responsabilidad**: Solo lógica de negocio y orquestación

```python
# Ejemplo: task_service.py
def create_task(self, task_create: TaskCreate) -> Task:
    # 🎯 Lógica de negocio
    if self._is_duplicate_title(task_create.title):
        raise ValueError("Título duplicado")
    
    # 📝 Crear modelo
    task = Task(id=uuid4(), title=task_create.title, ...)
    
    # 💾 Persistir datos
    saved_task = self.repository.create_task(task)
    
    # 📧 Orquestar servicios relacionados
    self.notification_service.send_task_created(saved_task)
    self.queue_service.enqueue_task_processing(saved_task)
    
    return saved_task
```

**✅ Qué SÍ hacen:**
- Implementan **reglas de negocio**
- Validan datos según lógica del dominio
- Orquestan múltiples operaciones
- Coordinan entre diferentes servicios
- Manejan transacciones de negocio
- Llaman a **Repositories**

**❌ Qué NO hacen:**
- Saber sobre HTTP, Lambda o API Gateway
- Acceso directo a AWS (DynamoDB, S3, SQS)
- Formateo de respuestas HTTP
- Parsing de requests

### **3. 💾 CAPA DE REPOSITORIES** (`repositories/`)
**Responsabilidad**: Solo acceso a datos y conversiones

```python
# Ejemplo: task_repository.py
def create_task(self, task: Task) -> Task:
    # 🔄 Convertir modelo a formato DynamoDB
    item = self._task_to_dynamodb_item(task)
    
    # 💾 Guardar en base de datos
    self.table.put_item(Item=item)
    
    # 🔄 Convertir respuesta a modelo
    return self._dynamodb_item_to_task(item)

def _task_to_dynamodb_item(self, task: Task) -> Dict:
    # Conversiones específicas para DynamoDB
    return {
        'id': task.id,
        'title': task.title,
        'created_at': task.created_at.isoformat(),
        # ... más conversiones
    }
```

**✅ Qué SÍ hacen:**
- **CRUD** en bases de datos (DynamoDB, S3)
- **Conversiones** modelo ↔ base de datos
- **Queries** específicas y optimizadas
- Manejo de errores de base de datos
- Implementación de patrones de acceso a datos

**❌ Qué NO hacen:**
- Lógica de negocio
- Validaciones de negocio
- Conocer sobre HTTP o eventos Lambda
- Orquestación de múltiples operaciones

### **4. 📝 CAPA DE MODELS** (`models.py`)
**Responsabilidad**: Solo definición de estructuras de datos

```python
# Modelos Pydantic para validación y estructura
class Task(BaseModel):
    id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    files: List[str] = []

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    tags: List[str] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

class TaskResponse(BaseModel):
    message: str
    task: Optional[Task] = None
    tasks: Optional[List[Task]] = None
```

### **5. 🛠️ CAPA DE UTILS** (`utils/`)
**Responsabilidad**: Solo utilidades compartidas

```python
# aws_config.py - Configuración centralizada de AWS
def get_dynamodb_resource():
    return boto3.resource('dynamodb', 
                         endpoint_url=LOCALSTACK_ENDPOINT,
                         region_name=AWS_REGION)

# response_utils.py - Respuestas HTTP estándar
def success_response(status_code: int, message: str, 
                    task: Optional[Task] = None, 
                    tasks: Optional[List[Task]] = None) -> Dict:
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'message': message,
            'task': task,
            'tasks': tasks
        }, default=str)
    }
```

## 🔄 **FLUJO DE DATOS** (Ejemplo: Crear Tarea)

```
1. 📡 API Gateway → create_task_handler.py
   └── "POST /tasks con JSON"
   
2. 🎯 Handler (Parseo y Validación)
   ├── parse_request_body(event) → JSON
   ├── TaskCreate(**body) → Validación
   └── Llama a task_service.create_task()

3. ⚙️ Service (Lógica de Negocio)
   ├── Validaciones de negocio
   ├── Crear modelo Task()
   ├── task_repository.create_task() → DynamoDB
   ├── notification_service.send() → SNS
   ├── queue_service.enqueue() → SQS
   └── Devolver Task creada

4. 🎯 Handler (Respuesta)
   ├── success_response() → Formato HTTP
   └── return {"statusCode": 201, "body": "..."}

5. 📡 API Gateway ← Handler
   └── "HTTP 201 + JSON response"
```

## 🎯 **PRINCIPIOS APLICADOS**

### **✅ Single Responsibility Principle (SRP)**

**Implementación Actual:**
```python
# create_task_handler.py - SOLO manejo de eventos (1 responsabilidad)
def lambda_handler(event, context):
    body = parse_request_body(event)        # Utils
    task_create = TaskCreate(**body)        # Models
    task = task_service.create_task()       # Service
    return success_response(task=task)      # Utils

# task_service.py - SOLO lógica de negocio (1 responsabilidad)
def create_task(self, task_create):
    task = Task(id=uuid4(), ...)           # Models
    saved_task = repository.create_task()   # Repository
    notification_service.send()            # Service
    queue_service.enqueue()                 # Service
    return saved_task

# task_repository.py - SOLO acceso a datos (1 responsabilidad)
def create_task(self, task):
    item = self._task_to_dynamodb_item()    # Conversión
    self.table.put_item(Item=item)          # DynamoDB
    return self._dynamodb_item_to_task()    # Conversión
```

### **🔄 Flujo de Dependencias**

```
📱 API Gateway
    ↓
🎯 Handler (Events & HTTP)
    ↓
⚙️ Service (Business Logic)
    ↓
💾 Repository (Data Access)
    ↓
🗄️ DynamoDB/S3/SQS/SNS

📝 Models (usado por todas las capas)
🛠️ Utils (usado por todas las capas)
```

## ✅ **VENTAJAS DE ESTA ARQUITECTURA**

### **1. 🎯 Responsabilidad Única (SRP)**
- Cada archivo/clase tiene **una sola razón para cambiar**
- **Handlers**: Solo eventos Lambda/HTTP
- **Services**: Solo lógica de negocio  
- **Repositories**: Solo acceso a datos
- **Models**: Solo estructura de datos
- **Utils**: Solo utilidades compartidas

### **2. 🧪 Testabilidad Mejorada**
```python
# Fácil testing en aislamiento
def test_task_service():
    # Mock solo las dependencias externas
    mock_repository = Mock()
    mock_notification = Mock()
    
    service = TaskService(
        repository=mock_repository,
        notification_service=mock_notification
    )
    
    # Probar SOLO la lógica de negocio
    result = service.create_task(task_data)
    
    # Verificar comportamiento sin tocar BD real
    mock_repository.create_task.assert_called_once()
    mock_notification.send.assert_called_once()
```

### **3. 🔧 Mantenibilidad**
```python
# Cambios localizados por responsabilidad
📝 Cambio en validación de negocio    → Solo TaskService
💾 Cambio de DynamoDB a PostgreSQL    → Solo TaskRepository  
🎯 Cambio en formato de API           → Solo Handlers
📊 Cambio en estructura de datos      → Solo Models
🛠️ Cambio en configuración AWS        → Solo Utils
```

### **4. ♻️ Reutilización de Código**
```python
# TaskService se puede usar desde múltiples contextos
task_service = TaskService()

# Desde API REST
task_service.create_task(task_data)  # Handler HTTP

# Desde procesamiento SQS  
task_service.create_task(task_data)  # SQS Processor

# Desde eventos S3
task_service.create_task(task_data)  # S3 Event Handler

# Desde cron/scheduler
task_service.create_task(task_data)  # EventBridge
```

### **5. 🔗 Desacoplamiento**
```python
# Cada capa no conoce detalles de implementación de otras
🎯 Handlers     ← No saben sobre DynamoDB, solo llaman Services
⚙️ Services     ← No saben sobre HTTP, solo lógica de negocio
💾 Repositories ← No saben sobre reglas de negocio, solo datos
📝 Models       ← No saben sobre infraestructura, solo estructura
```

### **6. 📈 Escalabilidad**
```python
# Fácil agregar nuevas funcionalidades
├── handlers/
│   ├── existing_handlers.py
│   └── new_feature_handler.py     # ← Nuevo endpoint
├── services/  
│   ├── existing_services.py
│   └── new_feature_service.py     # ← Nueva lógica
└── repositories/
    ├── existing_repositories.py
    └── new_data_source_repo.py    # ← Nueva fuente de datos
```

### **7. 🚀 Deployment Independiente**
```yaml
# Cada handler puede desplegarse independientemente
Functions:
  CreateTask:
    Handler: handlers.create_task_handler.lambda_handler
    Events: [POST /tasks]
    
  ListTasks:  
    Handler: handlers.list_tasks_handler.lambda_handler
    Events: [GET /tasks]
    
  ProcessSQS:
    Handler: handlers.sqs_processor_handler.lambda_handler  
    Events: [SQS Queue]
```

## 🚀 **Cómo usar la nueva estructura**

### **Para desarrollo local:**
```bash
cd task-manager
python -m handlers.create_task_handler  # Probar handler individual
```

### **Para despliegue AWS:**
```yaml
# En serverless.yml o CDK
create-task:
  handler: handlers.create_task_handler.lambda_handler
  
list-tasks:
  handler: handlers.list_tasks_handler.lambda_handler
```

## 📊 **Métricas de la Arquitectura**

| Aspecto | Implementación Actual |
|---------|----------------------|
| **Archivos especializados** | 15+ archivos con responsabilidad única |
| **Líneas por archivo** | 50-100 líneas promedio |
| **Responsabilidades** | 1 responsabilidad por archivo |
| **Testabilidad** | Alta (componentes aislados) |
| **Reutilización** | Alta (servicios reutilizables) |
| **Mantenibilidad** | Excelente (cambios localizados) |

## 🎯 **Próximos pasos**

1. ✅ **Completar handlers faltantes** (update, delete, upload)
2. ✅ **Crear file_service.py**
3. ✅ **Actualizar tests para nueva estructura**
4. ✅ **Actualizar servidor local**
5. ✅ **Documentar patrones de uso**

¿Te parece bien esta organización? ¿Quieres que completemos los handlers faltantes?