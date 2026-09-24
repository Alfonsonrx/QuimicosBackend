# 008 — Perfil propio (/me)

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| TEC-008 | Alfonsonrx | 2026-09-24 | 2026-09-24 | Hecho |

## Descripción
Cualquier usuario autenticado obtiene sus datos básicos para guardarlos en el frontend al iniciar sesión.

## Actor
Usuario

## Precondiciones
- El usuario debe haber ingresado (JWT válido).

## Flujo normal
1. Tras el login, el frontend llama `GET /accounts_api/users/me/`.
2. El sistema retorna `id`, `name`, `first_lastname`, `type`.

## Flujo alterno
—

## Excepciones
- Sin token → `401`.

## Postcondiciones
El frontend conoce la identidad y el tipo del usuario.

## Estado en el backend
- `UserViewSet.me` (`accounts/views.py`) con `SelfUserSerializer` (`accounts/serializers.py`), solo lectura.
- `SelfUserSerializer` se mantiene mínimo a propósito; el perfil completo lo ve el admin en `/users/{id}/`.
