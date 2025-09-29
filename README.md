# 🚀 TaskManager Serverless AWS

Sistema de gestión de tareas serverless con arquitectura por capas, AWS CDK y desarrollo local con FastAPI.

## ⭐ Características Principales

- ✅ **CRUD completo** de tareas con validación robusta
- 📎 **Archivos adjuntos** en S3 con gestión automática  
- 🔔 **Notificaciones** SNS/SQS para eventos del sistema
- 🏗️ **Arquitectura limpia** por capas (Handlers → Services → Repositories)
- 🐳 **Entorno local** completo con LocalStack (sin AWS real)
- 🚀 **Infraestructura como código** con AWS CDK Python

## 🏗️ Arquitectura

```
📱 API Gateway ➜ ⚡ Lambda Functions ➜ 🗄️ DynamoDB
                      ⬇️
                  📦 S3 Files ➜ 🔔 SNS ➜ 📨 SQS
```

**Servicios AWS:**
- **DynamoDB**: Almacenamiento de tareas con GSI
- **Lambda**: 6 funciones (CRUD + SQS processor)  
- **API Gateway**: REST API con CORS
- **S3**: Archivos adjuntos con versioning
- **SNS/SQS**: Notificaciones asíncronas con DLQ

## 🚀 Inicio Rápido

### Desarrollo Local
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar LocalStack
python local/setup_localstack.py

# 3. Ejecutar servidor local
python local/api_server.py
# ➜ http://localhost:8000/docs
```

### Deploy AWS (Producción)  
```bash
# 1. Configurar AWS CLI
aws configure

# 2. Clonar con submódulos
git clone --recursive https://github.com/SantiagoEsquivelHub/TaskManagerServerless_AWS.git

# 3. Bootstrap CDK (solo primera vez)
cd cdk && cdk bootstrap

# 3. Desplegar infraestructura
cdk deploy
```

## 📁 Estructura del Proyecto

```
📦 TaskManagerServerless_AWS/
├── 🔧 cdk/                     # Infraestructura AWS CDK
│   ├── cdk_stack.py           # Stack principal con todos los recursos
│   ├── deploy.ps1             # Script automatizado de deploy
│   └── DEPLOYMENT_GUIDE.md    # Guía completa de despliegue
├── ⚡ lambdas/                # Funciones Lambda
│   ├── handlers/              # Controladores HTTP
│   ├── services/             # Lógica de negocio
│   ├── repositories/         # Acceso a datos
│   └── models.py             # Modelos Pydantic
├── 🐳 local/                  # Desarrollo local
│   ├── api_server.py         # FastAPI server
│   ├── setup_localstack.py   # Configuración LocalStack
│   └── test_*.py             # Pruebas locales
└── 📊 monitoring/             # Herramientas de monitoreo
    ├── sns_monitor.py        # Monitor SNS en tiempo real
    └── diagnose_sns.py       # Diagnósticos completos
```

## 🛠️ Tecnologías

**Backend:**
- Python 3.9+ con Pydantic
- FastAPI para desarrollo local
- AWS Lambda para producción

**Infraestructura:**
- AWS CDK (Python) para IaC
- LocalStack para desarrollo local
- PowerShell scripts para automatización

**Base de datos:**
- DynamoDB con índices GSI
- S3 para archivos estáticos

## 📋 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/tasks` | Listar tareas con filtros |
| `POST` | `/tasks` | Crear nueva tarea |
| `PUT` | `/tasks/{id}` | Actualizar tarea |
| `DELETE` | `/tasks/{id}` | Eliminar tarea |
| `POST` | `/tasks/{id}/upload` | Subir archivo |

**Filtros disponibles:** `status`, `priority`, `tags`, `created_after`, `created_before`

## 🔍 Monitoreo y Debugging

```bash
# Monitor SNS en tiempo real
python monitoring/sns_monitor.py

# Diagnóstico completo del sistema
python monitoring/diagnose_sns.py

# Logs de Lambda (producción)
aws logs tail /aws/lambda/task-manager-createtask --follow
```

## � Estructura de Submódulos

Este proyecto utiliza **submódulos Git** para separar la infraestructura del código de aplicación:

- **📱 Aplicación**: `TaskManagerServerless_AWS` (este repo)
- **🏗️ Infraestructura**: `TaskManagerServerless_CDK` (submódulo en `/cdk`)

### Trabajar con Submódulos
```bash
# Clonar proyecto completo
git clone --recursive https://github.com/SantiagoEsquivelHub/TaskManagerServerless_AWS.git

# Actualizar submódulos existentes
git submodule update --recursive

# Actualizar submódulo a latest
cd cdk && git pull origin main && cd .. && git add cdk && git commit -m "Update CDK submodule"
```

## �📚 Documentación Adicional

- 📖 [Guía de Despliegue](cdk/DEPLOYMENT_GUIDE.md) - Deploy paso a paso
- 🏗️ [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) - Diagramas de arquitectura
- 🔄 [SEQUENCE_DIAGRAM.md](SEQUENCE_DIAGRAM.md) - Flujos de operaciones
- 🌐 [INFRASTRUCTURE_DIAGRAM.md](INFRASTRUCTURE_DIAGRAM.md) - Infraestructura AWS
- 💰 [Análisis de Costos](cdk/COST_ANALYSIS.md) - Estimación de costos
- 🔧 [TaskManagerServerless_AWS.md](TaskManagerServerless_AWS.md) - Especificaciones técnicas

## 🎯 Próximos Pasos

- [ ] Frontend React/Vue conectado al API
- [ ] Autenticación con AWS Cognito
- [ ] CI/CD pipeline con GitHub Actions
- [ ] Métricas y dashboards en CloudWatch
- [ ] Tests de integración automatizados

---

💡 **Tip**: Usa `python local/api_server.py` para desarrollo rápido sin AWS