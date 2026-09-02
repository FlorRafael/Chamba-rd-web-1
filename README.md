# 🇩🇴 CHAMBA RD — Plataforma Profesional de Servicios en República Dominicana

**CHAMBA RD** es una solución integral diseñada para conectar clientes con técnicos y trabajadores independientes en toda la República Dominicana.

---

## 🏛️ Arquitectura del Sistema

```
┌────────────────────────────────────────────────────────┐
│               CHAMBA RD FRONTEND (Android)             │
│        Jetpack Compose • Kotlin • Material 3           │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTPS / REST (JSON)
                           ▼
┌────────────────────────────────────────────────────────┐
│               CHAMBA RD BACKEND (Render)               │
│              FastAPI • Python 3.11+ • Uvicorn          │
│  JWT Auth • Escrow Payments • Verifications • Chat     │
└──────────────────────────┬─────────────────────────────┘
                           │ SQLAlchemy 2.0 / Alembic
                           ▼
┌────────────────────────────────────────────────────────┐
│            POSTGRESQL DATABASE (Render DB)             │
│   Users, Chambas, Postulaciones, Pagos, Reseñas, etc.  │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Despliegue en Render con PostgreSQL

### 1. Despliegue Automático con `render.yaml`
El proyecto incluye un archivo `render.yaml` listo para **Blueprint Infrastructure as Code**:
1. Entra a tu cuenta en [Render.com](https://render.com).
2. Haz clic en **New +** y selecciona **Blueprint**.
3. Conecta tu repositorio de GitHub de `CHAMBA RD`.
4. Render aprovisionará automáticamente:
   * **Base de Datos Administrada PostgreSQL** (`chambard-db`).
   * **Web Service API** (`chamba-rd-api`).
   * Aplicación automática de migraciones con Alembic en el Build Command.

### 2. Configuración Manual en Render (Si no usas Blueprints)
* **Crear Base de Datos PostgreSQL**:
  * Name: `chambard-db`
  * Database: `chambard`
  * User: `chamba_user`
  * Plan: Free / Starter
* **Crear Web Service**:
  * Name: `chamba-rd-api`
  * Environment: `Python`
  * Build Command: `pip install -r requirements.txt && alembic upgrade head && python backend/seed.py`
  * Start Command: `gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
  * **Environment Variables**:
    * `DATABASE_URL`: Pegar el *Internal Database URL* proporcionado por la BD de Render.
    * `SECRET_KEY`: Tu clave secreta generada (ej: `openssl rand -hex 32`).
    * `DEFAULT_COMMISSION_RATE`: `0.10` (10% de comisión configurable).
    * `ENVIRONMENT`: `production`

---

## 💻 Ejecución Local del Backend

### Requisitos Previos
* Python 3.10 o superior
* Servidor PostgreSQL local o instancia remota

### Pasos:
```bash
# 1. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales de PostgreSQL

# 4. Ejecutar migraciones de base de datos
alembic upgrade head

# 5. Poblar datos iniciales dominicanos (categorías, tarifas RD$, admin)
python backend/seed.py

# 6. Iniciar servidor de desarrollo
uvicorn backend.main:app --reload --port 8000
```

Accede a la documentación interactiva Swagger en: `http://localhost:8000/docs`

---

## 📦 Subir el Proyecto a GitHub

```bash
# 1. Inicializar repositorio git (si no está inicializado)
git init

# 2. Agregar archivos
git add .

# 3. Confirmar cambios
git commit -m "feat: Integración de producción CHAMBA RD (Android + FastAPI + PostgreSQL)"

# 4. Conectar a tu repositorio remoto en GitHub
git remote add origin https://github.com/TU_USUARIO/chamba-rd.git
git branch -M main

# 5. Enviar código a GitHub
git push -u origin main
```

---

## 👥 Sistema de Roles y Creación Segura de Administradores

CHAMBA RD implementa una separación estricta entre los roles públicos de la plataforma y el rol administrativo interno.

### 1. Roles Públicos (Registro Abierto)
* 👤 **Cliente (`cliente`)**: Persona o empresa que publica ofertas de trabajo (chambas), evalúa propuestas, contrata técnicos y efectúa pagos en custodia.
* 👷 **Técnico (`tecnico` / `trabajador`)**: Profesional independiente que postula sus servicios, fija presupuestos en RD$, chatea con clientes y envía su Cédula JCE y diploma de INFOTEP para verificación.

> 🔒 **Blindaje de Registro Público**: El endpoint `POST /api/v1/auth/register` y los formularios de la app rechazan terminantemente cualquier valor que intente registrar usuarios como `admin`. Los usuarios no pueden auto-asignarse privilegios administrativos.

### 2. Rol Interno (Administrador del Sistema)
* 🛡️ **Administrador (`admin`)**: Acceso exclusivo al panel de control, estadísticas de ingresos y volumen en RD$, aprobación/rechazo de verificaciones oficiales, resolución de disputas y configuración de comisiones.

### 3. Creación Segura del Primer Administrador
El primer administrador se crea durante la inicialización del backend (`backend/seed.py`) mediante variables de entorno protegidas:
1. En el Dashboard de Render (o archivo `.env` local), configura:
   ```env
   ADMIN_EMAIL=tu_correo_admin@tudominio.com
   ADMIN_PASSWORD=TuContrasenaSeguraYPrivada2026!
   ```
2. Al ejecutarse el build (`python backend/seed.py`):
   * El sistema verifica si ya existe un administrador en la base de datos.
   * Si no existe, genera el usuario con contraseña encriptada (Bcrypt) y activa la bandera `must_change_password=True`.
   * Si ya existe un administrador, **no duplica ni sobreescribe** la cuenta existente.
   * Las contraseñas **nunca se escriben en el código**, ni se imprimen en logs de servidor.

### 4. Administradores Adicionales
Una vez inicializado el sistema, los nuevos administradores sólo pueden ser creados o promovidos por un administrador autenticado mediante el endpoint protegido:
`POST /api/v1/admin/administradores` (requiere token JWT con rol `admin`).

---

## 📡 Catálogo de Endpoints de la API REST (`/api/v1`)

| Módulo | Método | Ruta | Descripción | Rol Requerido |
| :--- | :---: | :--- | :--- | :---: |
| **Autenticación** | `POST` | `/auth/register` | Registro de clientes y técnicos | Público |
| | `POST` | `/auth/login` | Inicio de sesión con JWT | Público |
| | `GET` | `/auth/me` | Perfil del usuario autenticado | Autenticado |
| | `PUT` | `/auth/profile` | Actualización de perfil profesional | Autenticado |
| | `PUT` | `/auth/change-password` | Cambio de contraseña segura | Autenticado |
| **Chambas** | `POST` | `/chambas/` | Publicar nueva chamba con fotos y RD$ | Cliente / Admin |
| | `GET` | `/chambas/` | Búsqueda y filtros de chambas disponibles | Público |
| | `GET` | `/chambas/{id}` | Detalle completo de una chamba | Público |
| | `PUT` | `/chambas/{id}/cancel` | Cancelar publicación | Cliente / Admin |
| **Postulaciones** | `POST` | `/postulaciones/` | Postularse con propuesta y precio en RD$ | Técnico |
| | `GET` | `/postulaciones/chamba/{id}` | Ver candidatos postulados | Cliente dueño |
| | `POST` | `/postulaciones/{id}/select` | Adjudicar y contratar técnico ganador | Cliente dueño |
| **Verificación** | `POST` | `/verificaciones/solicitar` | Enviar Cédula JCE y certificación INFOTEP | Técnico |
| | `GET` | `/verificaciones/pendientes` | Lista de solicitudes por moderar | Admin |
| | `POST` | `/verificaciones/{id}/aprobar` | Aprobar y otorgar insignia oficial | Admin |
| | `POST` | `/verificaciones/{id}/rechazar` | Rechazar solicitud con motivo | Admin |
| **Pagos (Escrow)** | `POST` | `/pagos/iniciar` | Iniciar pago en custodia para la chamba | Cliente |
| | `POST` | `/pagos/{id}/liberar` | Liberar fondos al técnico al completar | Cliente / Admin |
| | `GET` | `/pagos/summary/worker` | Resumen de ingresos y comisiones | Técnico |
| **Mensajería** | `POST` | `/chat/` | Enviar mensaje dentro de la chamba | Participantes |
| | `GET` | `/chat/chamba/{id}` | Historial de conversación | Participantes |
| **Estimador RD$** | `GET` | `/estimador/referencias` | Catálogo oficial de tarifas dominicanas | Público |
| | `POST` | `/estimador/calcular` | Calculadora por unidades, m², puntos | Público |
| **Administración** | `GET` | `/admin/stats` | Métricas y KPIs de la plataforma | Admin |
| | `GET` | `/admin/administradores` | Lista de administradores del sistema | Admin |
| | `POST` | `/admin/administradores` | Crear/promover nuevo administrador | Admin |
| | `PUT` | `/admin/administradores/{id}/status` | Activar o desactivar administrador | Admin |
| | `PUT` | `/admin/config/commission` | Modificar comisión de CHAMBA RD | Admin |
| | `PUT` | `/admin/users/{id}/suspend` | Suspender o reactivar usuario | Admin |

---

## 💳 Servicios Externos para Producción

1. **Pasarela de Pagos Dominicana**: Para cobros en tarjeta de crédito/débito en RD$ se recomienda conectar la integración bancaria con **CardNET**, **Azul (Banco Popular)** o **PixelPay**. El modelo de base de datos (`Payment`) ya cuenta con los campos de custodia (`retenido`, `liberado`), comisión porcentual y referencia externa (`transaction_ref`).
2. **Almacenamiento de Archivos (Fotos & Cédula)**: Para producción en la nube, se recomienda utilizar un bucket de **Amazon S3** o **Cloudinary** para almacenar las imágenes de portafolio y comprobantes, guardando únicamente las URLs en PostgreSQL.
