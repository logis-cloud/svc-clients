from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from . import models, schemas


# ---------- Clientes ----------
def get_cliente(db: Session, cliente_id: int):
    return (
        db.query(models.Cliente)
        .options(joinedload(models.Cliente.direcciones))
        .filter(models.Cliente.id == cliente_id)
        .first()
    )


def get_cliente_by_email(db: Session, email: str):
    return db.query(models.Cliente).filter(models.Cliente.email == email).first()


def list_clientes(db: Session, skip: int = 0, limit: int = 50, activo: bool | None = None):
    query = db.query(models.Cliente)
    if activo is not None:
        query = query.filter(models.Cliente.activo == activo)
    return query.order_by(models.Cliente.id).offset(skip).limit(limit).all()


def count_clientes(db: Session):
    return db.query(models.Cliente).count()


def create_cliente(db: Session, cliente: schemas.ClienteCreate):
    data = cliente.model_dump(exclude={"direcciones"})
    db_cliente = models.Cliente(**data)
    for dir_data in cliente.direcciones:
        db_cliente.direcciones.append(models.Direccion(**dir_data.model_dump()))
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


def update_cliente(db: Session, cliente_id: int, cambios: schemas.ClienteUpdate):
    db_cliente = get_cliente(db, cliente_id)
    if not db_cliente:
        return None
    for campo, valor in cambios.model_dump(exclude_unset=True).items():
        setattr(db_cliente, campo, valor)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


def delete_cliente(db: Session, cliente_id: int):
    db_cliente = get_cliente(db, cliente_id)
    if not db_cliente:
        return None
    db.delete(db_cliente)
    db.commit()
    return db_cliente


# ---------- Direcciones ----------
def list_direcciones_by_cliente(db: Session, cliente_id: int):
    return (
        db.query(models.Direccion)
        .filter(models.Direccion.cliente_id == cliente_id)
        .all()
    )


def get_direccion(db: Session, direccion_id: int):
    return db.query(models.Direccion).filter(models.Direccion.id == direccion_id).first()


def create_direccion(db: Session, cliente_id: int, direccion: schemas.DireccionCreate):
    db_dir = models.Direccion(cliente_id=cliente_id, **direccion.model_dump())
    db.add(db_dir)
    db.commit()
    db.refresh(db_dir)
    return db_dir


def update_direccion(db: Session, direccion_id: int, cambios: schemas.DireccionUpdate):
    db_dir = get_direccion(db, direccion_id)
    if not db_dir:
        return None
    for campo, valor in cambios.model_dump(exclude_unset=True).items():
        setattr(db_dir, campo, valor)
    db.commit()
    db.refresh(db_dir)
    return db_dir


def delete_direccion(db: Session, direccion_id: int):
    db_dir = get_direccion(db, direccion_id)
    if not db_dir:
        return None
    db.delete(db_dir)
    db.commit()
    return db_dir
