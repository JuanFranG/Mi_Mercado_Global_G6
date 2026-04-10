# Mi Mercado Global — Documentación del Proyecto

## DATOS
Numero de grupo: 6
Integrantes:
Shania Russo            - 2021114030
Juan Francisco González - 2021114063
Samir Vides             - 2020114219

## Descripción General

Mi Mercado Global es una aplicación de e-commerce de demostración que muestra el perfil de un usuario, sus pedidos recientes y el detalle de cada pedido. Está construida sobre una arquitectura de tres capas: base de datos NoSQL (DynamoDB Local en Docker), API REST (FastAPI/Python) y frontend SPA (Vue 3).

---

## Estructura del Proyecto

```
Mi-mercado-global-main/
├── mi-mercado-global-back/        # API REST en Python
│   ├── main.py                    # Endpoints FastAPI
│   ├── dynamodb_adapter.py        # Adaptador de acceso a DynamoDB
│   ├── crear_tabla.py             # Script: crea la tabla y el GSI en DynamoDB
│   ├── insertar_datos.py          # Script: datos de Luisa (UUID 550e8400-...)
│   └── insertar_mas_datos.py      # Script: datos de Carlos (UUID a1b2c3d4-...)
│
├── mi-mercado-global-front/       # SPA en Vue 3 + Vite
│   ├── src/
│   │   ├── App.vue                # Componente raíz, layout principal
│   │   ├── main.ts                # Punto de entrada de Vue
│   │   ├── router/index.ts        # Rutas de la aplicación
│   │   ├── components/
│   │   │   ├── TheHeader.vue      # Encabezado con nombre, breadcrumb y reloj
│   │   │   ├── UserProfile.vue    # Tarjeta de perfil del usuario
│   │   │   ├── RecentOrders.vue   # Tabla de pedidos recientes del usuario
│   │   │   └── OrderDetail.vue    # Panel de detalle del pedido seleccionado
│   │   └── views/
│   │       └── HomeView.vue       # Vista principal (vacía, el layout está en App.vue)
│   ├── package.json
│   └── vite.config.ts
│
├── codigo_base.md                 # Este archivo
└── modelado_mi_mercado_global.md  # Diseño del modelo de datos DynamoDB
```

---

## Flujo Completo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│  Docker                                                      │
│  amazon/dynamodb-local  →  expone puerto 8000               │
│  Emula la API de AWS DynamoDB localmente                     │
└────────────────────┬────────────────────────────────────────┘
                     │  HTTP (protocolo DynamoDB Wire)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  dynamodb_adapter.py                                         │
│  boto3.resource(endpoint_url="http://localhost:8000")        │
│  Genera KeyConditionExpression, PutItem, UpdateItem, etc.    │
│  Encapsula toda interacción con la base de datos             │
└────────────────────┬────────────────────────────────────────┘
                     │  Python (llamadas a métodos del adaptador)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  main.py  —  FastAPI                                         │
│  Recibe peticiones HTTP REST                                 │
│  Llama al adaptador y devuelve JSON                          │
│  Corre en  http://localhost:8001                             │
└────────────────────┬────────────────────────────────────────┘
                     │  HTTP/JSON (fetch desde el navegador)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Vue 3 + Vite  —  Frontend                                   │
│  Corre en  http://localhost:5173                             │
│  Componentes: UserProfile, RecentOrders, OrderDetail         │
└─────────────────────────────────────────────────────────────┘
```

**Por qué funciona con Docker:** DynamoDB Local emula el protocolo de red de AWS DynamoDB. boto3 no distingue si habla con AWS o con el contenedor — solo cambia el `endpoint_url`. Las credenciales pueden ser cualquier string (se usan `"test"`/`"fake"` indistintamente en local).

---

## Modelo de Datos — Single-Table Design

La tabla `MiMercadoGlobal` almacena todos los tipos de entidades con una sola tabla, distinguiéndolas por el valor de las claves.

### Esquema de claves

| PK | SK | Entidad | Patrón de acceso |
|---|---|---|---|
| `USER#<uuid>` | `PERFIL` | Perfil del usuario | Ver nombre, email, direcciones, métodos de pago |
| `USER#<uuid>` | `ORD#<fecha>#<num>` | Referencia de pedido en el usuario | Listar pedidos del usuario ordenados por fecha |
| `ORD#<num>` | `INFO` | Cabecera del pedido | Ver estado, total, dirección de envío |
| `ORD#<num>` | `ITEM#<ref>` | Línea de producto del pedido | Ver productos, cantidades, precios del pedido |

### Por qué el pedido aparece dos veces

El item `USER#<uuid> + ORD#<fecha>#<num>` permite listar todos los pedidos de un usuario ordenados cronológicamente (DynamoDB ordena el SK lexicográficamente).

El item `ORD#<num> + INFO` permite acceder directamente al detalle del pedido con solo su ID numérico, sin necesidad de conocer el usuario. Esta duplicidad es una práctica estándar en Single-Table Design.

### GSI_1 — Búsqueda por estado

Permite consultar todos los pedidos en un estado determinado sin escanear la tabla completa.

| Configuración | Valor |
|---|---|
| Nombre | `GSI_1` |
| PK del índice | `Estado` (String) |
| SK del índice | `Fecha_Creacion` (String ISO 8601) |
| Proyección | `ALL` |

```
Query GSI_1: Estado = "Enviado"
→ devuelve todos los pedidos enviados, ordenados por fecha
```

### TTL — Expiración automática

Los pedidos con estado `Cancelado` incluyen el atributo `expira_en` (timestamp Unix). DynamoDB los elimina automáticamente al vencer, sin operaciones manuales de borrado.

---

## Backend — FastAPI + Python

### Dependencias

```
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.13.0
boto3==1.42.76
botocore==1.42.76
click==8.3.1
fastapi==0.135.2
h11==0.16.0
idna==3.11
jmespath==1.1.0
pydantic==2.12.5
pydantic_core==2.41.5
python-dateutil==2.9.0.post0
s3transfer==0.16.0
six==1.17.0
starlette==1.0.0
typing-inspection==0.4.2
typing_extensions==4.15.0
urllib3==2.6.3
uvicorn==0.42.0
```

### Endpoints disponibles

| Método | URL | Descripción |
|---|---|---|
| `GET` | `/api/usuarios/{uuid}/perfil` | Devuelve nombre, email, direcciones y métodos de pago |
| `GET` | `/api/usuarios/{uuid}/pedidos` | Lista los pedidos del usuario ordenados por fecha desc |
| `GET` | `/api/pedidos/{id}` | Devuelve cabecera + líneas de producto del pedido |
| `GET` | `/api/pedidos?estado=Enviado` | Filtra pedidos por estado usando GSI_1 |
| `PATCH` | `/api/pedidos/{id}/estado?estado=Entregado` | Actualiza solo el campo Estado de un pedido |

### DynamoDB Adapter (`dynamodb_adapter.py`)

Centraliza toda interacción con la base de datos. `main.py` nunca llama a boto3 directamente.

| Método del adaptador | Query que genera |
|---|---|
| `obtener_perfil(usuario_id)` | `PK = USER#<id> AND SK = PERFIL` |
| `listar_pedidos_usuario(usuario_id)` | `PK = USER#<id> AND SK begins_with ORD#` |
| `obtener_detalle_pedido(id_pedido)` | `PK = ORD#<id>` (todas las SK) |
| `buscar_pedidos_por_estado(estado)` | GSI_1: `Estado = <estado>` |
| `actualizar_estado_pedido(id, estado)` | `UpdateItem` solo campo `Estado` |
| `insertar_lote(items)` | `BatchWriter` con múltiples `PutItem` |
| `eliminar_item(pk, sk)` | `DeleteItem` por clave primaria |

### Datos de prueba incluidos

**Luisa** — `insertar_datos.py`
- UUID: `550e8400-e29b-41d4-a716-446655440000`
- Pedidos: `#554`, `#555`, `#556`

**Carlos Alberto** — `insertar_mas_datos.py`
- UUID: `a1b2c3d4-e5f6-7890-1234-56789abcdef0`
- Pedidos: `#901`, `#902`

> **Importante sobre credenciales:** Los scripts de inserción usan `aws_access_key_id='fake'` y `main.py`/`crear_tabla.py` usan `aws_access_key_id='test'`. En DynamoDB Local esto no importa (no valida credenciales). Sin embargo, si tu contenedor Docker fue iniciado con credenciales específicas o usas variables de entorno distintas, debes unificar el valor en todos los archivos Python para evitar confusión.

---

## Cómo Levantar el Proyecto

Requiere tres terminales abiertas simultáneamente.

### Prerequisitos

- Docker instalado y corriendo
- Python 3.x (Anaconda o sistema)
- Node.js v20+ con npm

---

### Terminal 1 — Base de datos (DynamoDB Local en Docker)

```bash
docker run -p 8000:8000 amazon/dynamodb-local
```

DynamoDB queda disponible en `http://localhost:8000`. Déjalo corriendo.

---

### Terminal 2 — Backend (FastAPI)

```bash
cd mi-mercado-global-back

# 1. (Opcional) Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows

# 2. Instalar dependencias
pip install fastapi uvicorn boto3

# 3. Crear la tabla en DynamoDB (solo la primera vez)
python crear_tabla.py

# 4. Insertar datos de prueba (solo la primera vez)
python insertar_datos.py
python insertar_mas_datos.py

# 5. Levantar el servidor en el puerto 8001
#    (8000 ya está ocupado por DynamoDB Local)
uvicorn main:app --reload --port 8001
```

El backend queda disponible en `http://localhost:8001`.  
Puedes verificarlo en `http://localhost:8001/docs` (Swagger UI generado por FastAPI).

> **Nota:** Si usas Anaconda y ya tienes las dependencias instaladas globalmente, puedes omitir los pasos 1 y 2 y ejecutar `uvicorn` directamente.

---

### Terminal 3 — Frontend (Vue 3 + Vite)

Requiere Node.js instalado. El frontend usa Vue 3 como framework de componentes y Vite como bundler/servidor de desarrollo.

```bash
cd mi-mercado-global-front

# Instalar dependencias del proyecto
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend queda disponible en `http://localhost:5173`.

---

## Frontend — Vue 3 + Vite

### Componentes

| Componente | Responsabilidad |
|---|---|
| `App.vue` | Layout raíz. Define el UUID del usuario activo y el pedido seleccionado. Distribuye props a los componentes hijos. |
| `TheHeader.vue` | Encabezado con el nombre de la app, breadcrumb de navegación y reloj en tiempo real (actualización cada minuto). |
| `UserProfile.vue` | Muestra nombre, email, direcciones y métodos de pago del usuario. Consulta `GET /api/usuarios/{uuid}/perfil`. |
| `RecentOrders.vue` | Tabla de pedidos recientes. Al hacer clic en una fila emite el ID del pedido seleccionado hacia `App.vue`. Consulta `GET /api/usuarios/{uuid}/pedidos`. |
| `OrderDetail.vue` | Panel de detalle del pedido activo. Reacciona a cambios en el pedido seleccionado vía `watch`. Consulta `GET /api/pedidos/{id}`. |

### Tecnologías del frontend

| Paquete | Versión | Rol |
|---|---|---|
| `vue` | ^3.5 | Framework reactivo de componentes |
| `vue-router` | ^5.0 | Enrutamiento SPA |
| `pinia` | ^3.0 | Manejo de estado global (disponible, no usado aún) |
| `vite` | ^7.0 | Servidor de desarrollo y bundler |
| `typescript` | ~5.9 | Tipado estático |

---

## Usuarios de Prueba

Para probar la aplicación en el navegador, el UUID activo está definido directamente en `App.vue`:

```vue
<UserProfile usuarioId="550e8400-e29b-41d4-a716-446655440000" />
```

Para cambiar al usuario Carlos, reemplaza el UUID en `App.vue` por:

```
a1b2c3d4-e5f6-7890-1234-56789abcdef0
```

---

## Resumen de Puertos

| Servicio | Puerto | URL |
|---|---|---|
| DynamoDB Local (Docker) | 8000 | `http://localhost:8000` |
| FastAPI (Backend) | 8001 | `http://localhost:8001` |
| Vite (Frontend) | 5173 | `http://localhost:5173` |
| Swagger UI (Docs API) | 8001 | `http://localhost:8001/docs` |
