```mermaid
graph LR
    subgraph "🌍 AWS CLOUD us-east-1"
        subgraph "🏢 AVAILABILITY ZONES"
            subgraph "📍 AZ-1a"
                AZ1[🏗️ Infrastructure<br/>Auto-distributed]
            end
            subgraph "📍 AZ-1b" 
                AZ2[🏗️ Infrastructure<br/>Auto-distributed]
            end
            subgraph "📍 AZ-1c"
                AZ3[🏗️ Infrastructure<br/>Auto-distributed]
            end
        end

        subgraph "🌐 EDGE LOCATIONS"
            CF[☁️ CloudFront<br/>Optional<br/>Global CDN]
            EDGE1[📍 Edge Location 1]
            EDGE2[📍 Edge Location 2]
            EDGE3[📍 Edge Location N]
        end

        subgraph "🔌 API LAYER"
            subgraph "🚪 API Gateway Service"
                APIGW_SVC[🌐 API Gateway<br/>Multi-AZ<br/>Managed Service]
                APIGW_CACHE[⚡ Response Caching<br/>Optional]
                APIGW_LOG[📝 Access Logs<br/>CloudWatch]
            end
        end

        subgraph "⚡ COMPUTE LAYER"
            subgraph "🖥️ Lambda Service Mesh"
                LAMBDA_SVC[⚡ Lambda Service<br/>Multi-AZ<br/>Auto-scaling]
                
                subgraph "🔄 Function Instances"
                    L_INST1[📝 CreateTask<br/>Container Instance]
                    L_INST2[📋 ListTasks<br/>Container Instance] 
                    L_INST3[✏️ UpdateTask<br/>Container Instance]
                    L_INST4[🗑️ DeleteTask<br/>Container Instance]
                    L_INST5[📎 UploadFile<br/>Container Instance]
                    L_INST6[🔄 SQSProcessor<br/>Container Instance]
                end
            end
        end

        subgraph "💾 STORAGE LAYER"
            subgraph "🗄️ DynamoDB Global Tables"
                DDB_SVC[🗄️ DynamoDB Service<br/>Multi-AZ<br/>3 Replicas minimum]
                
                subgraph "📊 Table Partitions"
                    PART1[📄 Partition 1<br/>Hash A-F]
                    PART2[📄 Partition 2<br/>Hash G-M]
                    PART3[📄 Partition 3<br/>Hash N-S]
                    PART4[📄 Partition 4<br/>Hash T-Z]
                end

                subgraph "📈 Global Secondary Indexes"
                    GSI1[📊 status-index<br/>Distributed partitions]
                    GSI2[📊 priority-index<br/>Distributed partitions]
                end
            end

            subgraph "📦 S3 Infrastructure"
                S3_SVC[📦 S3 Service<br/>99.999999999% durability]
                
                subgraph "🗂️ Storage Classes"
                    S3_STD[💎 Standard<br/>Frequent access]
                    S3_IA[💿 Infrequent Access<br/>Auto-transition]
                    S3_GLACIER[🧊 Glacier<br/>Long-term archive]
                end
            end
        end

        subgraph "📡 MESSAGING LAYER"
            subgraph "🔔 SNS Infrastructure"
                SNS_SVC[📡 SNS Service<br/>Multi-AZ<br/>Push notifications]
                SNS_TOPICS[📢 Topics<br/>Fan-out pattern]
            end

            subgraph "📨 SQS Infrastructure"  
                SQS_SVC[📨 SQS Service<br/>Multi-AZ<br/>Message durability]
                
                subgraph "📬 Queue Types"
                    SQS_STD[📬 Standard Queue<br/>At-least-once delivery]
                    SQS_DLQ[☠️ Dead Letter Queue<br/>Error handling]
                end
            end
        end

        subgraph "🛡️ SECURITY LAYER"
            subgraph "🔐 IAM Infrastructure"
                IAM_SVC[🛡️ IAM Service<br/>Global<br/>Policy enforcement]
                IAM_ROLES[👤 Roles and Policies<br/>Least privilege]
            end

            subgraph "🔒 Security Services"
                KMS[🔑 KMS<br/>Encryption keys]
                WAF[🛡️ WAF<br/>Optional<br/>Web filtering]
                SHIELD[🛡️ Shield<br/>DDoS protection]
            end
        end

        subgraph "📊 MONITORING LAYER"
            subgraph "☁️ CloudWatch Infrastructure"
                CW_SVC[☁️ CloudWatch<br/>Multi-AZ<br/>Metrics and Logs]
                
                subgraph "📈 Observability"
                    CW_METRICS[📊 Custom Metrics<br/>Real-time monitoring]
                    CW_LOGS[📝 Log Groups<br/>Centralized logging]
                    CW_ALARMS[🚨 Alarms<br/>Automated responses]
                end
            end

            subgraph "🔍 Distributed Tracing"
                XRAY_SVC[🔍 X-Ray<br/>Request tracing<br/>Performance analysis]
            end
        end

        subgraph "🏗️ DEPLOYMENT LAYER"
            subgraph "📋 CloudFormation"
                CF_SVC[📋 CloudFormation<br/>Infrastructure as Code]
                CF_STACKS[📚 Stacks<br/>Resource management]
            end

            subgraph "⚙️ CDK Infrastructure"
                CDK_CLI[⚙️ CDK CLI<br/>Developer tooling]
                CDK_ASSETS[📦 CDK Assets<br/>S3 storage]
            end
        end
    end

    %% External connections
    subgraph "🌍 INTERNET"
        USERS[👥 Global Users<br/>Web/Mobile clients]
        DEVS[👨‍💻 Developers<br/>CI/CD pipelines]
    end

    %% Connections
    USERS -->|HTTPS| CF
    CF -->|Cache Miss| APIGW_SVC
    USERS -.->|Direct| APIGW_SVC
    
    DEVS -->|cdk deploy| CDK_CLI
    CDK_CLI -->|CloudFormation| CF_SVC
    CF_SVC -->|Provisions| APIGW_SVC
    CF_SVC -->|Provisions| LAMBDA_SVC
    CF_SVC -->|Provisions| DDB_SVC
    CF_SVC -->|Provisions| S3_SVC
    CF_SVC -->|Provisions| SNS_SVC
    CF_SVC -->|Provisions| SQS_SVC

    APIGW_SVC -->|Invoke| LAMBDA_SVC
    LAMBDA_SVC -->|Read/Write| DDB_SVC
    LAMBDA_SVC -->|Store Files| S3_SVC
    LAMBDA_SVC -->|Publish| SNS_SVC
    SNS_SVC -->|Fan-out| SQS_SVC
    SQS_SVC -->|Trigger| LAMBDA_SVC

    %% Multi-AZ distribution
    LAMBDA_SVC -.->|Auto-distributed| AZ1
    LAMBDA_SVC -.->|Auto-distributed| AZ2
    LAMBDA_SVC -.->|Auto-distributed| AZ3
    DDB_SVC -.->|Replicated| AZ1
    DDB_SVC -.->|Replicated| AZ2
    DDB_SVC -.->|Replicated| AZ3
    S3_SVC -.->|Replicated| AZ1
    S3_SVC -.->|Replicated| AZ2
    S3_SVC -.->|Replicated| AZ3

    %% Security
    IAM_SVC -.->|Permissions| LAMBDA_SVC
    IAM_SVC -.->|Permissions| DDB_SVC
    IAM_SVC -.->|Permissions| S3_SVC
    IAM_SVC -.->|Permissions| SNS_SVC
    IAM_SVC -.->|Permissions| SQS_SVC
    KMS -.->|Encryption| DDB_SVC
    KMS -.->|Encryption| S3_SVC
    KMS -.->|Encryption| SNS_SVC
    KMS -.->|Encryption| SQS_SVC

    %% Monitoring
    LAMBDA_SVC -->|Metrics/Logs| CW_SVC
    APIGW_SVC -->|Access Logs| CW_SVC
    DDB_SVC -->|Metrics| CW_SVC
    S3_SVC -->|Access Logs| CW_SVC

    LAMBDA_SVC -.->|Tracing| XRAY_SVC

    %% Styling
    classDef awsService fill:#ff9800,stroke:#e65100,stroke-width:2px,color:#fff
    classDef storage fill:#4caf50,stroke:#1b5e20,stroke-width:2px,color:#fff
    classDef compute fill:#2196f3,stroke:#0d47a1,stroke-width:2px,color:#fff
    classDef network fill:#9c27b0,stroke:#4a148c,stroke-width:2px,color:#fff
    classDef security fill:#f44336,stroke:#b71c1c,stroke-width:2px,color:#fff
    classDef monitoring fill:#607d8b,stroke:#263238,stroke-width:2px,color:#fff
    classDef external fill:#795548,stroke:#3e2723,stroke-width:2px,color:#fff

    class DDB_SVC,S3_SVC storage
    class LAMBDA_SVC,L_INST1,L_INST2,L_INST3,L_INST4,L_INST5,L_INST6 compute
    class APIGW_SVC,SNS_SVC,SQS_SVC,CF network
    class IAM_SVC,KMS,WAF,SHIELD security
    class CW_SVC,XRAY_SVC,CW_METRICS,CW_LOGS monitoring
    class USERS,DEVS external
```

## 🏗️ **Infraestructura Física AWS - TaskManager Serverless**

### 🌍 **Distribución Geográfica**

| Capa | Multi-AZ | Replicación | Durabilidad |
|------|----------|-------------|-------------|
| **API Gateway** | ✅ Automática | 3+ AZ | 99.95% SLA |
| **Lambda** | ✅ Automática | Todas las AZ | 99.95% SLA |
| **DynamoDB** | ✅ Automática | 3+ replicas | 99.999999999% |
| **S3** | ✅ Automática | Cross-AZ | 99.999999999% |
| **SNS/SQS** | ✅ Automática | Multi-AZ | 99.9% SLA |

### ⚡ **Características de Escalabilidad**

#### 🔄 **Auto-Scaling Automático**
- **Lambda**: 0 → 1000 concurrent executions en segundos
- **DynamoDB**: Auto-scaling basado en demanda
- **API Gateway**: 10,000+ RPS por región  
- **S3**: Virtually unlimited storage
- **SNS/SQS**: Millions de mensajes por segundo

#### 📊 **Particionamiento Inteligente**
- **DynamoDB**: Hash partitioning automático por task_id
- **S3**: Distribución automática por prefijo
- **Lambda**: Container reuse + warm starts
- **API Gateway**: Edge-optimized endpoints

### 🛡️ **Resiliencia y Recuperación**

#### ⚠️ **Failure Handling**
```
AZ Failure → Automatic failover (< 30s)
Lambda Error → Retry + DLQ pattern  
DDB Throttling → Exponential backoff
S3 Error → Built-in retry logic
API Timeout → Circuit breaker pattern
```

#### 🔄 **Disaster Recovery**
- **RTO**: < 15 minutes (Recovery Time Objective)
- **RPO**: < 1 minute (Recovery Point Objective)  
- **Backup**: Point-in-time recovery available
- **Cross-Region**: Can be extended for global deployment

### 💰 **Optimización de Costos por Capa**

| Servicio | Modelo de Costo | Optimización |
|----------|-----------------|--------------|
| **Lambda** | Pay-per-invocation + duration | Function warming, memory tuning |
| **DynamoDB** | Pay-per-request | On-demand billing, GSI optimization |
| **S3** | Pay-per-storage + requests | Lifecycle policies, intelligent tiering |
| **API Gateway** | Pay-per-request | Caching, request optimization |
| **SNS/SQS** | Pay-per-message | Batch processing, message deduplication |

---
*Diagrama de infraestructura física completa - AWS Multi-AZ Deployment*