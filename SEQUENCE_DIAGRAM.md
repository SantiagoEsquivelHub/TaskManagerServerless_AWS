```mermaid
sequenceDiagram
    participant User as 👤 Cliente
    participant API as 🌐 API Gateway
    participant CreateLambda as ⚡ CreateTask
    participant ListLambda as ⚡ ListTasks
    participant UpdateLambda as ⚡ UpdateTask
    participant UploadLambda as ⚡ UploadFile
    participant DDB as 🗄️ DynamoDB
    participant S3 as 📦 S3 Bucket
    participant SNS as 📡 SNS Topic
    participant SQS as 📨 SQS Queue
    participant Processor as 🔄 SQS Processor

    %% Crear Tarea
    Note over User,Processor: 📝 FLUJO: Crear Nueva Tarea
    User->>+API: POST /tasks<br/>{title, description, priority}
    API->>+CreateLambda: Invoke con payload
    CreateLambda->>+DDB: PutItem con task_id único
    DDB-->>-CreateLambda: Success
    CreateLambda->>+SNS: Publish "task_created" event
    SNS-->>-CreateLambda: MessageId
    CreateLambda-->>-API: 201 Created + task data
    API-->>-User: HTTP 201 + JSON response
    
    %% Notificación asíncrona
    SNS->>+SQS: Forward message (fan-out)
    SQS->>+Processor: Trigger (batch of 1-10 msgs)
    Processor->>Processor: Process "task_created" event
    Processor->>+DDB: Optional: Update metrics
    DDB-->>-Processor: Success
    Processor-->>-SQS: Delete message from queue

    %% Listar Tareas
    Note over User,Processor: 📋 FLUJO: Listar Tareas con Filtros
    User->>+API: GET /tasks?status=pending&priority=high
    API->>+ListLambda: Invoke con query params
    ListLambda->>+DDB: Query status-index<br/>FilterExpression: priority
    DDB-->>-ListLambda: Items array
    ListLambda->>ListLambda: Format response + pagination
    ListLambda-->>-API: 200 OK + tasks array
    API-->>-User: HTTP 200 + JSON response

    %% Subir Archivo
    Note over User,Processor: 📎 FLUJO: Subir Archivo a Tarea
    User->>+API: POST /tasks/{id}/upload<br/>Content-Type: multipart/form-data
    API->>+UploadLambda: Invoke con file data
    UploadLambda->>+DDB: GetItem para verificar task existe
    DDB-->>-UploadLambda: Task data
    UploadLambda->>+S3: PutObject con file key único
    S3-->>-UploadLambda: ETag + metadata
    UploadLambda->>+DDB: UpdateItem: add file_key to task
    DDB-->>-UploadLambda: Success
    UploadLambda->>+SNS: Publish "file_uploaded" event
    SNS-->>-UploadLambda: MessageId
    UploadLambda-->>-API: 200 OK + file metadata
    API-->>-User: HTTP 200 + upload success

    %% Actualizar Tarea
    Note over User,Processor: ✏️ FLUJO: Actualizar Estado de Tarea
    User->>+API: PUT /tasks/{id}<br/>{status: "completed"}
    API->>+UpdateLambda: Invoke con task_id + updates
    UpdateLambda->>+DDB: GetItem para obtener estado actual
    DDB-->>-UpdateLambda: Current task data
    UpdateLambda->>+DDB: UpdateItem con nuevos valores
    DDB-->>-UpdateLambda: Updated attributes
    UpdateLambda->>+SNS: Publish "task_updated" event<br/>{old_status, new_status}
    SNS-->>-UpdateLambda: MessageId
    UpdateLambda-->>-API: 200 OK + updated task
    API-->>-User: HTTP 200 + JSON response

    %% Procesamiento asíncrono avanzado
    SNS->>+SQS: Forward "task_updated" message
    SQS->>+Processor: Trigger con event data
    
    alt Status = "completed"
        Processor->>Processor: Log completion metrics
        Processor->>+DDB: Update completion statistics
        DDB-->>-Processor: Success
    else Status = "cancelled"  
        Processor->>Processor: Handle cancellation logic
        Processor->>+S3: Optional: Archive associated files
        S3-->>-Processor: Success
    end
    
    Processor-->>-SQS: Delete processed message

    %% Error Handling
    Note over User,Processor: ⚠️ MANEJO DE ERRORES
    alt Lambda Error
        CreateLambda->>CreateLambda: Exception occurred
        CreateLambda-->>API: 500 Internal Server Error
        API-->>User: HTTP 500 + error details
    end
    
    alt SQS Processing Error
        SQS->>Processor: Message delivery (attempt 1)
        Processor->>Processor: Processing fails
        Processor-->>SQS: Error (message remains)
        SQS->>SQS: Wait visibility timeout
        SQS->>Processor: Message delivery (attempt 2)
        Processor-->>SQS: Error again
        SQS->>SQS: After 3 failed attempts
        SQS->>SQS: Send to Dead Letter Queue
    end
```

## 🔄 **Flujo de Datos TaskManager Serverless**

### 📊 **Patrones de Arquitectura Implementados**

1. **🎯 API Gateway Pattern**: Punto único de entrada con proxy integration
2. **⚡ Function-as-a-Service**: Funciones Lambda especializadas por operación
3. **🔄 Event-Driven Architecture**: SNS/SQS para procesamiento asíncrono
4. **📊 CQRS Ligero**: Separación read/write con índices optimizados
5. **🛡️ Security by Design**: IAM roles con permisos mínimos

### 🎭 **Scenarios de Uso Detallados**

#### 📝 **Crear Tarea**
```
Input: POST /tasks {"title": "Nueva tarea", "priority": "high"}
Process: Lambda → DynamoDB → SNS → SQS → Processor
Output: 201 Created + task_id + timestamp
Side Effects: Notificación asíncrona procesada
```

#### 📋 **Listar con Filtros**
```  
Input: GET /tasks?status=pending&priority=high&limit=10
Process: Lambda → DynamoDB GSI Query + Filter
Output: 200 OK + paginated results + next_token
Performance: Sub-100ms con índices optimizados
```

#### 📎 **Upload de Archivos**
```
Input: POST /tasks/123/upload + multipart file
Process: Lambda → S3 PutObject → DynamoDB UpdateItem → SNS
Output: 200 OK + file_url + metadata
Storage: S3 con versioning y lifecycle policies
```

### 🔒 **Seguridad Multi-Capa**

- **🌐 API Gateway**: Rate limiting, CORS, request validation
- **⚡ Lambda**: Execution role con permisos mínimos
- **🗄️ DynamoDB**: Encryption at rest, fine-grained access
- **📦 S3**: Bucket policies, object-level permissions
- **🔔 SNS/SQS**: Topic/queue policies, encryption en tránsito

---
*Diagrama de secuencia detallado - TaskManager Serverless AWS*