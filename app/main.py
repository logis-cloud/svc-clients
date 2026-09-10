from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microservicio de Clientes - Logística y Entregas",
    description=(
        "API REST para la gestión de clientes y sus direcciones de entrega. "
        "Parte del sistema distribuido de Logística y Entregas (CS2032 - Cloud Computing)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "ms-clientes"}


# ======================= CLIENTES =======================

@app.get("/clientes", response_model=list[schemas.ClienteListOut], tags=["Clientes"])
def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """Lista clientes de forma paginada. Filtro opcional por estado activo/inactivo."""
    return crud.list_clientes(db, skip=skip, limit=limit, activo=activo)


@app.get("/clientes/{cliente_id}", response_model=schemas.ClienteOut, tags=["Clientes"])
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle de un cliente, incluyendo sus direcciones registradas."""
    db_cliente = crud.get_cliente(db, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente


@app.post(
    "/clientes",
    response_model=schemas.ClienteOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Clientes"],
)
def crear_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    """Crea un nuevo cliente, opcionalmente con una o más direcciones iniciales."""
    if crud.get_cliente_by_email(db, cliente.email):
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    return crud.create_cliente(db, cliente)


@app.put("/clientes/{cliente_id}", response_model=schemas.ClienteOut, tags=["Clientes"])
def actualizar_cliente(
    cliente_id: int, cambios: schemas.ClienteUpdate, db: Session = Depends(get_db)
):
    """Actualiza parcialmente los datos de un cliente."""
    db_cliente = crud.update_cliente(db, cliente_id, cambios)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente


@app.delete("/clientes/{cliente_id}", tags=["Clientes"])
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Elimina un cliente y sus direcciones asociadas (cascade)."""
    db_cliente = crud.delete_cliente(db, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"detail": "Cliente eliminado correctamente"}


# ======================= DIRECCIONES =======================
# Consumidas típicamente por el microservicio de Envíos para saber
# dónde entregar el paquete de un cliente.

@app.get(
    "/clientes/{cliente_id}/direcciones",
    response_model=list[schemas.DireccionOut],
    tags=["Direcciones"],
)
def listar_direcciones(cliente_id: int, db: Session = Depends(get_db)):
    """Lista todas las direcciones de un cliente (usado por el microservicio de Envíos)."""
    if not crud.get_cliente(db, cliente_id):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return crud.list_direcciones_by_cliente(db, cliente_id)


@app.post(
    "/clientes/{cliente_id}/direcciones",
    response_model=schemas.DireccionOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Direcciones"],
)
def crear_direccion(
    cliente_id: int, direccion: schemas.DireccionCreate, db: Session = Depends(get_db)
):
    """Agrega una nueva dirección a un cliente existente."""
    if not crud.get_cliente(db, cliente_id):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return crud.create_direccion(db, cliente_id, direccion)


@app.put(
    "/direcciones/{direccion_id}",
    response_model=schemas.DireccionOut,
    tags=["Direcciones"],
)
def actualizar_direccion(
    direccion_id: int, cambios: schemas.DireccionUpdate, db: Session = Depends(get_db)
):
    db_dir = crud.update_direccion(db, direccion_id, cambios)
    if not db_dir:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return db_dir


@app.delete("/direcciones/{direccion_id}", tags=["Direcciones"])
def eliminar_direccion(direccion_id: int, db: Session = Depends(get_db)):
    db_dir = crud.delete_direccion(db, direccion_id)
    if not db_dir:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return {"detail": "Dirección eliminada correctamente"}
