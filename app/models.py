from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Cliente(Base):
    """
    Tabla: clientes
    Entidad principal. Relación 1:N con direcciones.
    """
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    telefono = Column(String(20), nullable=True)
    dni = Column(String(15), unique=True, nullable=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    activo = Column(Boolean, default=True)

    direcciones = relationship(
        "Direccion", back_populates="cliente", cascade="all, delete-orphan"
    )


class Direccion(Base):
    """
    Tabla: direcciones
    Relación N:1 con clientes (FK cliente_id).
    Usada por el microservicio de Envíos para saber a dónde entregar el paquete.
    """
    __tablename__ = "direcciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    calle = Column(String(200), nullable=False)
    distrito = Column(String(100), nullable=False)
    ciudad = Column(String(100), nullable=False)
    codigo_postal = Column(String(15), nullable=True)
    referencia = Column(String(200), nullable=True)
    tipo = Column(String(20), default="casa")  # casa | trabajo | otro
    es_principal = Column(Boolean, default=False)

    cliente = relationship("Cliente", back_populates="direcciones")
