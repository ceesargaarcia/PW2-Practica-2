"""
Script para crear el primer usuario administrador.

Uso:
    python create_admin.py
    python create_admin.py --username admin --email admin@test.com --password Admin123

Este script escribe directamente en la base de datos sin pasar por la API,
precisamente porque la API pública no permite crear admins por diseño (seguridad).
"""

import argparse
import sys
import os

# Asegurar que el directorio raíz del proyecto está en el path
sys.path.insert(0, os.path.dirname(__file__))

from db.database import SessionLocal, engine, Base
import models.user    # noqa: F401 — necesario para que Base registre la tabla
import models.product # noqa: F401

from repositories.user_repository import UserRepository
from models.user import UserRole


def create_admin(username: str, email: str, password: str) -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        repo = UserRepository(db)

        if repo.get_by_email(email):
            print(f"[!] Ya existe un usuario con email '{email}'.")
            sys.exit(1)

        if repo.get_by_username(username):
            print(f"[!] Ya existe un usuario con username '{username}'.")
            sys.exit(1)

        user = repo.create(
            username=username,
            email=email,
            plain_password=password,
            role=UserRole.admin,
        )

        print(f"[✓] Admin creado correctamente:")
        print(f"    username : {user.username}")
        print(f"    email    : {user.email}")
        print(f"    role     : {user.role.value}")
        print(f"    id       : {user.id}")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crear usuario administrador")
    parser.add_argument("--username", default="admin",        help="Nombre de usuario (default: admin)")
    parser.add_argument("--email",    default="admin@test.com", help="Email (default: admin@test.com)")
    parser.add_argument("--password", default="Admin123",     help="Contraseña (default: Admin123)")
    args = parser.parse_args()

    create_admin(args.username, args.email, args.password)
