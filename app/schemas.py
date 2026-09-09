from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Direccion ----------
class DireccionBase(BaseModel):
    calle: str
    distrito: str
    ciudad: str
    codigo_postal: Optional[str] = None
    referencia: Optional[str] = None
    tipo: Optional[str] = "casa"
    es_principal: Optional[bool] = False


class DireccionCreate(DireccionBase):
    pass


class DireccionUpdate(BaseModel):
    calle: Optional[str] = None
    distrito: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    referencia: Optional[str] = None
    tipo: Optional[str] = None
    es_principal: Optional[bool] = None


class DireccionOut(DireccionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int


# ---------- Cliente ----------
class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    telefono: Optional[str] = None
    dni: Optional[str] = None


class ClienteCreate(ClienteBase):
    direcciones: Optional[List[DireccionCreate]] = []


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    dni: Optional[str] = None
    activo: Optional[bool] = None


class ClienteOut(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    fecha_registro: datetime
    direcciones: List[DireccionOut] = []


class ClienteListOut(BaseModel):
    """Versión resumida para listados paginados (sin direcciones, más liviana)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    apellido: str
    email: EmailStr
    telefono: Optional[str] = None
    activo: bool
