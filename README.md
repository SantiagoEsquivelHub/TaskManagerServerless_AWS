# 🚀## ✨ Características Principales

### **🎯 Funcionalidades de Negocio**
- ✅ **CRUD completo de tareas** (crear, leer, actualizar, eliminar)
- 📎 **Gestión de archivos** vinculados a tareas (S3)  
- 🔍 **Filtrado avanzado** por estado, prioridad, etiquetas y fechas
- 📊 **Estadísticas en tiempo real** (total, por estado, por prioridad)
- 📧 **Notificaciones automáticas** vía SNS al crear/actualizar
- ⚡ **Procesamiento asíncrono** con colas SQS

### **🏗️ Arquitectura & Código**
- 🎯 **Arquitectura en capas** (Handlers → Services → Repositories → Models)
- ♻️ **Principios SOLID** aplicados (especialmente SRP)
- 🔗 **Bajo acoplamiento** entre componentes
- 🧪 **Alta testabilidad** (mocks, inyección de dependencias)
- 📝 **Validación robusta** con Pydantic models

### **🛠️ Desarrollo & DevOps**
- 🐳 **Entorno local completo** con LocalStack (no requiere AWS real)
- 📚 **Documentación automática** con FastAPI/Swagger UI
- 🧪 **Suite de pruebas completa** (unitarias, integración, smoke tests)
- 📬 **Colección Postman** para testing manual
- 🚀 **Setup rápido** (< 5 minutos desde cero)r Serverless AWS

Una aplicación serverless robusta para gestión de tareas construida con **arquitectura en capas**, siguiendo principios SOLID y mejores prácticas de desarrollo. Implementada con AWS Lambda, DynamoDB, S3, SQS, SNS y desarrollo local con LocalStack.

## ✨ Características Principales

- ✅ **CRUD completo de tareas** con validación de datos
- 📎 **Gestión de archivos** vinculados a tareas (S3)  
- 📧 **Notificaciones automáticas** vía SNS
- ⚡ **Procesamiento asíncrono** con colas SQS
- 🔍 **Filtrado avanzado** por estado, prioridad y etiquetas
- � **Estadísticas en tiempo real** de tareas  
- 🧪 **Entorno local completo** con LocalStack
- 🏗️ **Arquitectura en capas** (Handlers → Services → Repositories)
- 🧪 **Suite de pruebas completa** (unitarias + integración)
- 📚 **Documentación automática** con FastAPI/Swagger

## 🏗️ Arquitectura en Capas

### **Diagrama de Infraestructura**
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ API Gateway │────│ AWS Lambda   │────│ DynamoDB    │
│ (HTTP)      │    │ (Handlers)   │    │ (Tareas)    │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
                   ┌───────┼───────┐
                   │       │       │
              ┌────▼────┐ ┌▼──┐ ┌─▼─┐
              │   SNS   │ │SQS│ │S3 │
              │(Notif.) │ │   │ │   │
              └─────────┘ └───┘ └───┘
```

### **Patrón de Capas Implementado**
```
🎯 HANDLERS     → Solo eventos Lambda/HTTP
    ↓
⚙️ SERVICES     → Solo lógica de negocio  
    ↓
💾 REPOSITORIES → Solo acceso a datos
    ↓
📝 MODELS       → Solo estructura de datos
```

**Principio**: Cada capa tiene **una sola responsabilidad** y no conoce detalles de implementación de otras capas.

## 🛠️ Stack Tecnológico

### **Backend & Serverless**
- **Python 3.6+** (compatible con versiones legacy)
- **AWS Lambda** (Serverless functions)
- **Pydantic** (Validación y serialización de datos)
- **Boto3** (SDK de AWS para Python)

### **Almacenamiento & Datos**
- **DynamoDB** (Base de datos NoSQL)
- **S3** (Almacenamiento de archivos)

### **Mensajería & Notificaciones**
- **SQS** (Colas de mensajes asíncronos)
- **SNS** (Notificaciones push)

### **API & Desarrollo**
- **API Gateway** (Producción)
- **FastAPI** (Desarrollo local + documentación automática)
- **LocalStack** (Simulación AWS local)

### **Infraestructura & Deployment**
- **AWS CDK** (Infrastructure as Code)
- **Docker** (LocalStack containerization)

### **Testing & QA**
- **Pytest** (Framework de testing)
- **Postman Collection** (API testing)
- **Unittest.mock** (Mocking para pruebas unitarias)

## 📁 Estructura del Proyecto (Arquitectura en Capas)

```
TaskManagerServerless_AWS/
├── 📂 lambdas/                  # 🐍 Código Python principal
│   ├── 📝 models.py             # Modelos Pydantic (Task, TaskCreate, etc.)
│   ├── 📂 handlers/             # 🎯 CAPA: Controladores Lambda
│   │   ├── create_task_handler.py   # POST /tasks
│   │   ├── list_tasks_handler.py    # GET /tasks  
│   │   ├── update_task_handler.py   # PUT /tasks/{id}
│   │   ├── delete_task_handler.py   # DELETE /tasks/{id}
│   │   └── upload_file_handler.py   # POST /tasks/{id}/upload
│   ├── 📂 services/             # ⚙️ CAPA: Lógica de Negocio
│   │   ├── task_service.py          # CRUD + validaciones
│   │   ├── notification_service.py  # Notificaciones SNS
│   │   ├── queue_service.py         # Colas SQS
│   │   └── file_service.py          # Gestión archivos S3
│   ├── 📂 repositories/         # 💾 CAPA: Acceso a Datos
│   │   └── task_repository.py       # Operaciones DynamoDB
│   └── 📂 utils/                # 🛠️ CAPA: Utilidades
│       ├── aws_config.py            # Configuración AWS
│       └── response_utils.py        # Respuestas HTTP estándar
├── 📂 local/                    # 🖥️ Desarrollo Local
│   ├── api_server.py            # Servidor FastAPI (puerto 8000)
│   ├── setup_localstack.py     # Setup automático LocalStack
│   └── test_basic_functionality.py # Pruebas de smoke testing
├── 📂 tests/                    # 🧪 Suite de Pruebas
│   ├── test_lambda_functions.py     # Pruebas unitarias completas
│   └── test_complete_functionality.py # Pruebas integración + API
├── 📂 cdk/                      # ☁️ Infrastructure as Code
├── 📄 requirements.txt          # 📦 Dependencias Python
├── 📄 .env                      # 🔐 Variables de entorno
├── 📄 ARCHITECTURE.md           # 📚 Documentación arquitectura
├── 📄 TaskManager_API_Collection.postman_collection.json # 🧪 Postman
└── 📄 start_local.bat          # 🚀 Script inicio rápido
```

> **Nota**: La estructura sigue el **patrón de responsabilidad única** donde cada archivo/carpeta tiene una sola razón para cambiar.

## 🚀 Guía de Inicio Rápido

### 📋 Prerequisitos

| Herramienta | Versión | Propósito |
|-------------|---------|-----------|
| **Python** | 3.6+ | Runtime principal |
| **Docker** | Latest | LocalStack container |
| **Git** | Latest | Control de versiones |
| **Postman** | Optional | Testing API |

### 🏃‍♂️ Setup Rápido (< 5 minutos)

1. **📦 Clonar e instalar**:
```bash
git clone https://github.com/SantiagoEsquivelHub/TaskManagerServerless_AWS.git
cd TaskManagerServerless_AWS

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

2. **🐳 Iniciar LocalStack** (terminal separada):
```bash
# Instalar LocalStack si no lo tienes
pip install localstack

# Iniciar servicios AWS locales
localstack start
```

3. **⚡ Setup automático** (todo en uno):
```bash
# Windows - Script automático
start_local.bat

# Manual paso a paso
python local/setup_localstack.py  # Configura AWS local
python local/api_server.py        # Inicia API en puerto 8000
```

4. **✅ Verificar funcionamiento**:
- 🌐 **API Local**: http://localhost:8000
- 📚 **Documentación Swagger**: http://localhost:8000/docs  
- 💚 **Health Check**: http://localhost:8000/health
- 📊 **Estadísticas**: http://localhost:8000/tasks/statistics

### 🧪 Pruebas Rápidas

```bash
# Smoke tests básicos
python tests/test_complete_functionality.py --smoke

# Pruebas con Postman (importar colección)
# TaskManager_API_Collection.postman_collection.json

# Pruebas funcionales básicas
python test_basic_functionality.py
```

## 📝 Ejemplos de Uso

### **🌐 Usando la API Web (Recomendado)**
Visita http://localhost:8000/docs para la **interfaz Swagger interactiva** donde puedes probar todos los endpoints directamente desde el navegador.

### **💻 Ejemplos con cURL**

#### ✅ Crear una tarea
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implementar autenticación JWT",
    "description": "Agregar middleware de autenticación con tokens JWT",
    "priority": "high",
    "tags": ["backend", "security", "auth"]
  }'
```

#### 📋 Listar tareas con filtros
```bash
# Todas las tareas pendientes de alta prioridad
curl "http://localhost:8000/tasks?status=pending&priority=high&limit=10"

# Tareas con etiqueta específica
curl "http://localhost:8000/tasks?tag=backend&limit=5"
```

#### ✏️ Actualizar tarea
```bash
curl -X PUT "http://localhost:8000/tasks/{task_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "description": "Tarea actualizada - en progreso",
    "priority": "medium"
  }'
```

#### 📎 Subir archivo a tarea
```bash
curl -X POST "http://localhost:8000/tasks/{task_id}/upload" \
  -F "file=@documento.pdf" \
  -F "file=@imagen.jpg"
```

#### 📊 Obtener estadísticas
```bash
curl "http://localhost:8000/tasks/statistics"
```

### **🐍 Ejemplos con Python**
```python
import requests

# Crear tarea
response = requests.post('http://localhost:8000/tasks', json={
    'title': 'Tarea desde Python',
    'description': 'Creada usando requests',
    'priority': 'medium',
    'tags': ['python', 'automation']
})
print(f"Tarea creada: {response.json()}")

# Listar tareas
tasks = requests.get('http://localhost:8000/tasks?limit=5').json()
print(f"Total tareas: {len(tasks['tasks'])}")
```

## 🧪 Suite de Pruebas Completa

### **🔥 Smoke Tests (Verificación Rápida)**
```bash
# Pruebas básicas de funcionalidad (< 30 segundos)
python tests/test_complete_functionality.py --smoke

# Pruebas de funcionalidad básica
python test_basic_functionality.py
```

### **🔬 Pruebas Unitarias (Componentes Aislados)**
```bash
# Todas las pruebas unitarias con pytest
python -m pytest tests/test_complete_functionality.py -v

# Pruebas específicas por capa
python -m pytest tests/test_complete_functionality.py::TestTaskModels -v
python -m pytest tests/test_complete_functionality.py::TestTaskService -v
python -m pytest tests/test_complete_functionality.py::TestLambdaHandlers -v
```

### **🌐 Pruebas de Integración (API Completa)**
```bash
# Asegúrate de que la API local esté corriendo (puerto 8000)
python local/api_server.py

# En otra terminal - pruebas de integración
python -m pytest tests/test_complete_functionality.py::TestLocalAPIIntegration -v
```

### **📬 Pruebas con Postman**
1. Importar `TaskManager_API_Collection.postman_collection.json`
2. Verificar que API local esté en puerto 8000
3. Ejecutar colección completa (incluye tests automáticos)

### **📊 Cobertura de Pruebas**
- ✅ **Modelos Pydantic** (validación de datos)
- ✅ **Servicios de negocio** (lógica CRUD)
- ✅ **Repositorios** (acceso a DynamoDB)
- ✅ **Handlers Lambda** (controladores HTTP)
- ✅ **Utilidades** (respuestas, configuración)
- ✅ **API Integración** (end-to-end)

## 📊 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de la API |
| GET | `/health` | Health check |
| POST | `/tasks` | Crear tarea |
| GET | `/tasks` | Listar tareas (con filtros) |
| GET | `/tasks/{id}` | Obtener tarea específica |
| PUT | `/tasks/{id}` | Actualizar tarea |
| DELETE | `/tasks/{id}` | Eliminar tarea |
| POST | `/tasks/{id}/upload` | Subir archivo a tarea |
| GET | `/tasks/stats/summary` | Estadísticas de tareas |

### Parámetros de filtrado (GET /tasks)
- `status`: pending, in_progress, completed, cancelled
- `priority`: low, medium, high, critical
- `tag`: filtrar por etiqueta específica
- `limit`: número máximo de resultados (default: 50)

## 🔧 Configuración

### Variables de entorno (.env)
```env
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=tasks-table
S3_BUCKET_NAME=task-manager-files
SQS_QUEUE_URL=http://localhost:4566/000000000000/task-queue
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:000000000000:task-notifications
LOCALSTACK_ENDPOINT=http://localhost:4566
```

## 🚀 Despliegue en AWS

### Usando AWS CDK
```bash
# Instalar CDK
npm install -g aws-cdk

# Inicializar CDK (solo primera vez)
cdk bootstrap

# Desplegar infraestructura
cd cdk
cdk deploy
```

### Variables de entorno para producción
Actualizar `.env` con los valores reales de AWS después del despliegue.

## 📈 Monitoreo

### CloudWatch Logs
- Logs de cada función Lambda
- Métricas de performance
- Alertas por errores

### Métricas clave
- Número de tareas creadas por día
- Tiempo de respuesta de APIs
- Errores en procesamiento
- Uso de almacenamiento S3

## 🔐 Seguridad

- **IAM Roles** con permisos mínimos
- **API Keys** para proteger endpoints
- **Secrets Manager** para credenciales
- **S3 bucket** privado
- **Validación** de entrada con Pydantic

## �️ Documentación Adicional

- 📚 **[ARCHITECTURE.md](ARCHITECTURE.md)** - Documentación completa de la arquitectura en capas
- 📬 **[Postman Collection](TaskManager_API_Collection.postman_collection.json)** - Tests API automatizados
- 🧪 **[Tests](tests/)** - Suite completa de pruebas unitarias e integración

## 🛣️ Roadmap & Mejoras Futuras

### **🔐 Seguridad & Autenticación**
- [ ] **AWS Cognito** - Autenticación de usuarios
- [ ] **JWT Tokens** - Autorización por roles
- [ ] **API Keys** - Protección de endpoints públicos

### **📊 Funcionalidades Avanzadas**  
- [ ] **Paginación cursor-based** - Para listas grandes
- [ ] **Búsqueda full-text** - Con OpenSearch/Elasticsearch
- [ ] **Webhooks** - Notificaciones a sistemas externos
- [ ] **Bulk operations** - Operaciones masivas eficientes

### **🎨 Frontend & UX**
- [ ] **Dashboard React** - Interfaz web moderna
- [ ] **Mobile App** - React Native o Flutter
- [ ] **Real-time updates** - WebSockets para updates live

### **⚡ Performance & Escalabilidad**
- [ ] **ElastiCache** - Caché de consultas frecuentes  
- [ ] **DynamoDB Streams** - Procesamiento de eventos
- [ ] **Step Functions** - Workflows complejos
- [ ] **API GraphQL** - Consultas flexibles

### **🔧 DevOps & Monitoreo**
- [ ] **CI/CD Pipeline** - GitHub Actions
- [ ] **CloudWatch Dashboards** - Monitoreo visual
- [ ] **X-Ray Tracing** - Debugging distribuido
- [ ] **Load Testing** - Pruebas de carga automatizadas

## 🐛 Solución de problemas

### LocalStack no inicia
```bash
# Verificar Docker
docker ps

# Reiniciar LocalStack
localstack stop
localstack start
```

### Error de conexión a LocalStack
```bash
# Verificar que LocalStack esté ejecutándose
curl http://localhost:4566/_localstack/health
```

### Problemas con dependencias
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

## 📝 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Para contribuir:

1. **Fork** el proyecto
2. **Crear** rama de feature (`git checkout -b feature/NuevaFuncionalidad`)
3. **Commit** cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/NuevaFuncionalidad`)
5. **Abrir** Pull Request

### **� Guías de Contribución**
- Seguir la **arquitectura en capas** existente
- Agregar **pruebas** para nueva funcionalidad
- Actualizar **documentación** si es necesario
- Respetar **principios SOLID** y **clean code**

## 📧 Contacto & Autor

**Santiago Esquivel** - Desarrollador Full Stack  
- 🐙 **GitHub**: [@SantiagoEsquivelHub](https://github.com/SantiagoEsquivelHub)
- 💼 **LinkedIn**: [Conectar en LinkedIn](https://linkedin.com/in/santiago-esquivel-dev)
- 📧 **Email**: santiago.esquivel.dev@gmail.com

> 💡 **¿Preguntas sobre la arquitectura?** Revisa [ARCHITECTURE.md](ARCHITECTURE.md) o abre un issue en GitHub.