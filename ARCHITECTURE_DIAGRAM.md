```mermaid
graph TB
    %% Usuarios y Cliente
    subgraph "👥 USUARIOS"
        USER[👤 Cliente Web/Mobile]
        DEV[👨‍💻 Desarrollador]
    end

    %% API Gateway
    subgraph "🌐 API GATEWAY"
        APIGW[🚪 REST API<br/>task-manager-api<br/>CORS Enabled]
        
        subgraph "📍 ENDPOINTS"
            EP1[GET /tasks]
            EP2[POST /tasks]
            EP3[PUT /tasks/id]
            EP4[DELETE /tasks/id]
            EP5[POST /tasks/id/upload]
        end
    end

    %% Lambda Functions
    subgraph "⚡ LAMBDA FUNCTIONS"
        L1[📝 CreateTask<br/>Python 3.9<br/>256MB]
        L2[📋 ListTasks<br/>Python 3.9<br/>256MB]
        L3[✏️ UpdateTask<br/>Python 3.9<br/>256MB]
        L4[🗑️ DeleteTask<br/>Python 3.9<br/>256MB]
        L5[📎 UploadFile<br/>Python 3.9<br/>256MB]
        L6[🔄 SQSProcessor<br/>Python 3.9<br/>256MB]
    end

    %% Storage Layer
    subgraph "💾 ALMACENAMIENTO"
        subgraph "🗄️ DYNAMODB"
            DB[(📊 tasks-table<br/>Pay-per-request<br/>GSI status-index<br/>GSI priority-index)]
        end
        
        subgraph "📦 S3 BUCKET"
            S3[🗂️ task-manager-files<br/>Versioning ON<br/>Auto-delete ON<br/>CORS Enabled]
        end
    end

    %% Messaging & Notifications
    subgraph "🔔 MESSAGING"
        subgraph "📢 SNS"
            SNS[📡 task-notifications<br/>Topic]
        end
        
        subgraph "📨 SQS"
            SQS[📬 task-queue<br/>14 days retention<br/>300s visibility]
            DLQ[☠️ task-processing-dlq<br/>Dead Letter Queue<br/>Max retries 3]
        end
    end

    %% Security
    subgraph "🔐 SEGURIDAD"
        IAM[🛡️ TaskManagerLambdaRole<br/>DynamoDB RW<br/>S3 RWD<br/>SNS Publish<br/>SQS RWD<br/>CloudWatch Logs]
    end

    %% Monitoring
    subgraph "📊 MONITOREO"
        CW[☁️ CloudWatch<br/>Logs and Metrics]
        XRAY[🔍 X-Ray<br/>Distributed Tracing]
    end

    %% CDK Infrastructure
    subgraph "🏗️ INFRAESTRUCTURA COMO CÓDIGO"
        CDK[⚙️ AWS CDK<br/>Python Stack<br/>TaskManagerStack]
        CF[📋 CloudFormation<br/>Generated Template]
    end

    %% Connections - User Flow
    USER -->|HTTPS Requests| APIGW
    DEV -->|cdk deploy| CDK
    CDK -->|Generates| CF
    CF -->|Creates| APIGW
    CF -->|Creates| L1
    CF -->|Creates| L2
    CF -->|Creates| L3
    CF -->|Creates| L4
    CF -->|Creates| L5
    CF -->|Creates| L6
    CF -->|Creates| DB
    CF -->|Creates| S3
    CF -->|Creates| SNS
    CF -->|Creates| SQS
    CF -->|Creates| DLQ
    CF -->|Creates| IAM

    %% API Gateway to Lambda
    APIGW --> EP1
    APIGW --> EP2
    APIGW --> EP3
    APIGW --> EP4
    APIGW --> EP5
    
    EP1 -->|Proxy Integration| L2
    EP2 -->|Proxy Integration| L1
    EP3 -->|Proxy Integration| L3
    EP4 -->|Proxy Integration| L4
    EP5 -->|Proxy Integration| L5

    %% Lambda to Services
    L1 -->|PutItem/UpdateItem| DB
    L1 -->|Publish| SNS
    L2 -->|Query/Scan| DB
    L3 -->|UpdateItem/GetItem| DB
    L3 -->|Publish| SNS
    L4 -->|DeleteItem| DB
    L4 -->|DeleteObject| S3
    L4 -->|Publish| SNS
    L5 -->|PutObject| S3
    L5 -->|UpdateItem| DB
    L5 -->|Publish| SNS

    %% Messaging Flow
    SNS -->|Fan-out| SQS
    SQS -->|Event Source Mapping| L6
    SQS -.->|Failed messages| DLQ
    L6 -->|Process notifications| DB

    %% Security
    IAM -.->|Permissions| L1
    IAM -.->|Permissions| L2
    IAM -.->|Permissions| L3
    IAM -.->|Permissions| L4
    IAM -.->|Permissions| L5
    IAM -.->|Permissions| L6

    %% Monitoring
    L1 -->|Logs/Metrics| CW
    L2 -->|Logs/Metrics| CW
    L3 -->|Logs/Metrics| CW
    L4 -->|Logs/Metrics| CW
    L5 -->|Logs/Metrics| CW
    L6 -->|Logs/Metrics| CW
    
    L1 -.->|Tracing| XRAY
    L2 -.->|Tracing| XRAY
    L3 -.->|Tracing| XRAY
    L4 -.->|Tracing| XRAY
    L5 -.->|Tracing| XRAY
    L6 -.->|Tracing| XRAY

    %% Styling
    classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef apiClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef lambdaClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef storageClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef messageClass fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    classDef securityClass fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    classDef monitorClass fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef infraClass fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px

    class USER,DEV userClass
    class APIGW,EP1,EP2,EP3,EP4,EP5 apiClass
    class L1,L2,L3,L4,L5,L6 lambdaClass
    class DB,S3 storageClass
    class SNS,SQS,DLQ messageClass
    class IAM securityClass
    class CW,XRAY monitorClass
    class CDK,CF infraClass
```

## 🎯 **Arquitectura TaskManager Serverless AWS**

### 📊 **Flujo de Datos Principal**

1. **👤 Usuario** → **🌐 API Gateway** → **⚡ Lambda** → **🗄️ DynamoDB**
2. **📎 Archivos** → **⚡ Lambda** → **📦 S3 Bucket**
3. **🔔 Eventos** → **📡 SNS** → **📨 SQS** → **⚡ SQS Processor**

### 🔄 **Flujo de Notificaciones Asíncronas**

```
Crear Tarea → SNS Topic → SQS Queue → Lambda Processor
     ↓             ↓           ↓            ↓
  DynamoDB    Fan-out to   Batch of 10   Process &
   Insert     subscribers   messages      Update DB
```

### 🏗️ **Componentes Clave**

| Servicio | Propósito | Configuración |
|----------|-----------|---------------|
| **API Gateway** | Punto de entrada REST | CORS habilitado, 5 endpoints |
| **Lambda Functions** | Lógica de negocio | Python 3.9, 256MB, 30s timeout |
| **DynamoDB** | Base de datos NoSQL | Pay-per-request, 2 GSI |
| **S3** | Almacenamiento archivos | Versioning, auto-delete |
| **SNS/SQS** | Mensajería asíncrona | Topic + Queue + DLQ |
| **IAM** | Seguridad | Permisos mínimos necesarios |

### 💰 **Escalabilidad y Costos**

- **🔄 Auto-scaling**: Todos los servicios escalan automáticamente
- **💵 Pay-per-use**: Solo pagas por lo que usas
- **🆓 Free Tier**: Primer año muy económico
- **🧹 Destrucción**: `cdk destroy` → $0 inmediato

---
*Diagrama generado para TaskManager Serverless - AWS CDK Python Stack*