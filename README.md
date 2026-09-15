# Microservicio de Clientes — Sistema de Logística y Entregas

API REST (Python + FastAPI) para gestionar clientes y sus direcciones de entrega.
Es uno de los 3 microservicios "con base de datos propia" del proyecto
(los otros dos son Vehículos [Java/PostgreSQL] y Envíos [Node.js/MongoDB]).

Este microservicio **no genera ni carga datos ficticios**. Es una API REST
estándar: recibe requests, valida con Pydantic, y opera contra su base de
datos MySQL a través de SQLAlchemy. La carga masiva de datos de prueba
(≥20,000 registros exigidos por la rúbrica) es responsabilidad de una
herramienta externa (`seed-tool/`) que corre en la VM de bases de datos
(VM3), conectándose directamente a cada motor (MySQL, PostgreSQL, MongoDB)
por su IP privada — no del contenedor del microservicio.

## Diagrama Entidad/Relación (MySQL)

```
┌───────────────────────┐          ┌────────────────────────────┐
│        clientes        │ 1      N │         direcciones          │
├───────────────────────┤──────────├────────────────────────────┤
│ id (PK)               │          │ id (PK)                     │
│ nombre                │          │ cliente_id (FK -> clientes) │
│ apellido              │          │ calle                       │
│ email (UNIQUE)        │          │ distrito                    │
│ telefono              │          │ ciudad                      │
│ dni (UNIQUE)          │          │ codigo_postal                │
│ fecha_registro        │          │ referencia                   │
│ activo                │          │ tipo (casa/trabajo/otro)     │
└───────────────────────┘          │ es_principal                 │
                                    └────────────────────────────┘
```
Relación: **1 cliente → N direcciones** (`ON DELETE CASCADE`).

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/clientes` | Lista paginada de clientes |
| GET | `/clientes/{id}` | Detalle de un cliente + sus direcciones |
| POST | `/clientes` | Crea cliente (con direcciones opcionales) |
| PUT | `/clientes/{id}` | Actualiza datos de un cliente |
| DELETE | `/clientes/{id}` | Elimina cliente (cascade) |
| GET | `/clientes/{id}/direcciones` | Direcciones de un cliente (usado por el MS de Envíos) |
| POST | `/clientes/{id}/direcciones` | Agrega una dirección |
| PUT | `/direcciones/{id}` | Actualiza una dirección |
| DELETE | `/direcciones/{id}` | Elimina una dirección |

Swagger UI autogenerado: **`/docs`** — Redoc: **`/redoc`**

## Cómo correrlo en local

```bash
docker compose up --build
```

- API disponible en `http://localhost:8001`
- Swagger en `http://localhost:8001/docs`
- MySQL en `localhost:3306` (solo expuesto en desarrollo)

## Cargar datos ficticios (≥20,000 registros)

**No se hace desde este microservicio.** La carga masiva de datos de prueba
se ejecuta con la herramienta externa `seed-tool/`, ubicada fuera de este
repositorio, que corre en (o contra) la VM de bases de datos (VM3) y se
conecta directamente a `mysql-clientes` — así como a PostgreSQL (Vehículos)
y MongoDB (Envíos) — por IP privada, sin pasar por la API de ningún
microservicio. Ver el README de `seed-tool/` para las instrucciones de
ejecución.

Este microservicio se mantiene como una API estándar, sin dependencias de
generación de datos falsos ni endpoints/scripts de seeding en su código
fuente ni en su imagen Docker.

## Mapeo a la arquitectura de producción pedida en el enunciado

- Este contenedor (`ms-clientes`) se despliega junto a los otros 4
  microservicios en **2 Máquinas Virtuales** detrás de un **balanceador de
  carga privado**.
- Se expone al público solo a través de **AWS API Gateway (HTTPS)**.
- La base de datos MySQL de este microservicio corre en la **tercera MV**
  (privada, no pública), junto con PostgreSQL (Vehículos) y MongoDB (Envíos).
