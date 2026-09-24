# 005 — Crear usuarios

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| GU-01 | GG | 01-01-2024 | 2026-09-24 | Hecho |

## Descripción
El administrador debe ser capaz de crear usuarios, indicando su tipo (`empleado` por defecto o `administrador`). Crear un administrador exige reconfirmar la contraseña del administrador que lo crea.

## Actor
Usuario Administrador

## Precondiciones
- El usuario debe haber ingresado (JWT válido).
- El usuario debe ser tipo `administrador`.

## Flujo normal
1. El usuario selecciona “crear usuario”.
2. Ingresa los datos del nuevo usuario, incluido el tipo (opcional, `empleado` por defecto).
3. El sistema valida y guarda la información.
4. El sistema confirma la creación (`201`) y retorna los datos del usuario creado (`UserSerializer`).

## Flujo alterno
1. El administrador elige tipo `administrador`.
2. El sistema solicita su propia contraseña (`admin_password`).
3. El sistema la verifica con `request.user.check_password()`; si es correcta continúa el flujo normal desde el paso 3.

## Excepciones
- Contraseñas no coinciden, contraseña débil o email duplicado → `400`.
- No admin → `403`.
- `type=administrador` sin `admin_password` o con contraseña incorrecta → `403`, no se crea el usuario.

## Postcondiciones
El nuevo usuario queda registrado en el sistema (`is_active=True`, `type=empleado` por defecto).

## Estado en el backend
- `POST /accounts_api/registration/` → `CustomCreateView` (`accounts/views.py`), `UserCreateSerializer` (`accounts/serializers.py`); respuesta con `UserSerializer`.
- Verificación de contraseña en `check_admin_promotion` (`accounts/serializers.py`), compartida con [006](../006-modificar-usuario/spec.md).
- Tests en `accounts/tests.py` (`UserCreateAndPromotionTests`).
- Documentado en `API.md`.
