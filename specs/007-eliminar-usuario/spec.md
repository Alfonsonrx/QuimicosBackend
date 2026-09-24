# 007 — Eliminar usuarios

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| GU-03 | GG | 01-01-2024 | 2026-09-24 | Hecho |

## Descripción
El administrador debe ser capaz de eliminar usuarios.

## Actor
Usuario Administrador

## Precondiciones
- El usuario debe haber ingresado (JWT válido).
- El usuario debe ser tipo `administrador`.

## Flujo normal
1. El usuario selecciona “eliminar usuario”.
2. Selecciona el usuario a eliminar.
3. El frontend pide confirmación de la acción.
4. El sistema desactiva al usuario (`204`).

## Flujo alterno
—

## Excepciones
- Usuario inexistente → `404`.
- No admin → `403`.

## Postcondiciones
El usuario queda desactivado (`is_active=False`): no puede iniciar sesión y sale de los resúmenes; su historial de asistencia se conserva.

## Estado en el backend
- `DELETE /accounts_api/users/{id}/` → `UserViewSet.perform_destroy` (soft delete).
- Se eligió soft delete porque `AssistanceRecord.user` es `on_delete=CASCADE`: un borrado real eliminaría el historial.
- Reactivar: `PATCH /accounts_api/users/{id}/` con `{"is_active": true}`.
