# 006 — Modificar usuarios

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| GU-02 | GG | 01-01-2024 | 2026-09-24 | Hecho |

## Descripción
El administrador debe ser capaz de modificar usuarios.

## Actor
Usuario Administrador

## Precondiciones
- El usuario debe haber ingresado (JWT válido).
- El usuario debe ser tipo `administrador`.

## Flujo normal
1. El usuario selecciona “modificar usuario”.
2. Selecciona el usuario (`GET /accounts_api/users/`).
3. Actualiza los datos necesarios.
4. El sistema valida y guarda los cambios.
5. El sistema confirma la modificación (`200`).

## Flujo alterno
—

## Excepciones
- Datos inválidos o email duplicado → `400`.
- Usuario inexistente → `404`.
- No admin → `403`.
- Cambiar `type` a `administrador` sin `admin_password` válido → `403` (misma regla que [005](../005-crear-usuario/spec.md)).

## Postcondiciones
Los datos del usuario quedan actualizados.

## Estado en el backend
- `GET /accounts_api/users/`, `GET/PUT/PATCH /accounts_api/users/{id}/` → `UserViewSet` (`accounts/views.py`), `UserSerializer`.
- Tests en `accounts/tests.py`.
- La contraseña no se edita por este endpoint (fuera de alcance).
