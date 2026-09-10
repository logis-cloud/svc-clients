"""
Script de carga masiva (fake data) para el microservicio de Clientes.

Requisito del proyecto: insertar masivamente, por única vez, datos ficticios
en al menos 1 tabla (mínimo 20,000 registros). Aquí se cargan:
    - 25,000 clientes
    - ~30,000-50,000 direcciones (1 a 2 por cliente)

Uso:
    python seed_data.py            # corre dentro del contenedor / con la BD accesible
"""
import time
from faker import Faker
from sqlalchemy import text
from app.database import engine, SessionLocal, Base
from app import models

fake = Faker("es_PE")  # datos con formato/nombres en español (Perú)

TOTAL_CLIENTES = 25_000
BATCH_SIZE = 1_000
TIPOS_DIRECCION = ["casa", "trabajo", "otro"]


def crear_tablas():
    Base.metadata.create_all(bind=engine)


def generar_lote_clientes(n: int, offset: int):
    lote = []
    for i in range(n):
        idx = offset + i
        lote.append(
            {
                "nombre": fake.first_name(),
                "apellido": fake.last_name(),
                "email": f"{fake.user_name()}{idx}@example.com",
                "telefono": fake.phone_number()[:20],
                "dni": str(fake.unique.random_number(digits=8, fix_len=True)),
                "activo": True,
            }
        )
    return lote


def poblar():
    crear_tablas()
    db = SessionLocal()
    inicio = time.time()

    try:
        insertados = 0
        while insertados < TOTAL_CLIENTES:
            tam_lote = min(BATCH_SIZE, TOTAL_CLIENTES - insertados)
            lote_clientes = generar_lote_clientes(tam_lote, insertados)

            # bulk_insert_mappings es mucho más rápido que crear objetos ORM uno a uno
            db.bulk_insert_mappings(models.Cliente, lote_clientes)
            db.commit()

            insertados += tam_lote
            print(f"Clientes insertados: {insertados}/{TOTAL_CLIENTES}")

        # Ahora generamos direcciones para cada cliente (1 o 2 direcciones c/u)
        ids_clientes = [row[0] for row in db.query(models.Cliente.id).all()]
        lote_direcciones = []
        total_direcciones = 0

        for i, cliente_id in enumerate(ids_clientes):
            num_direcciones = 1 if i % 3 == 0 else 2  # variedad de escenarios
            for j in range(num_direcciones):
                lote_direcciones.append(
                    {
                        "cliente_id": cliente_id,
                        "calle": fake.street_address(),
                        "distrito": fake.city(),
                        "ciudad": "Lima",
                        "codigo_postal": fake.postcode(),
                        "referencia": fake.sentence(nb_words=6),
                        "tipo": TIPOS_DIRECCION[j % len(TIPOS_DIRECCION)],
                        "es_principal": (j == 0),
                    }
                )

            if len(lote_direcciones) >= BATCH_SIZE:
                db.bulk_insert_mappings(models.Direccion, lote_direcciones)
                db.commit()
                total_direcciones += len(lote_direcciones)
                print(f"Direcciones insertadas: {total_direcciones}")
                lote_direcciones = []

        if lote_direcciones:
            db.bulk_insert_mappings(models.Direccion, lote_direcciones)
            db.commit()
            total_direcciones += len(lote_direcciones)

        print(f"Direcciones insertadas: {total_direcciones}")
        print(f"Listo en {time.time() - inicio:.2f} segundos")

    finally:
        db.close()


if __name__ == "__main__":
    poblar()
