# 005 — Crear usuarios

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| GU-01 | GG | 01-01-2024 | 2026-09-24 | Hecho |

## Descripción
El administrador debe ser capaz de crear usuarios.

## Actor
Usuario Administrador

## Precondiciones
- El usuario debe haber ingresado (JWT válido).
- El usuario debe ser tipo `administrador`.

## Flujo normal
1. El usuario selecciona “crear usuario”.
2. Ingresa los datos del nuevo usuario.
3. El sistema valida y guarda la información.
4. El sistema confirma la creación (`201`).

## Flujo alterno
—

## Excepciones
- Contraseñas no coinciden, contraseña débil o email duplicado → `400`.
- No admin → `403`.

## Postcondiciones
El nuevo usuario queda registrado en el sistema (`is_active=True`, `type=empleado` por defecto).

## Estado en el backend
- `POST /accounts_api/registration/` → `CustomCreateView` (`accounts/views.py`), `UserCreateSerializer` (`accounts/serializers.py`).
- Documentado en `API.md`.
