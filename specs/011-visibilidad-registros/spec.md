# 011 — Visibilidad de registros de asistencia

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| TEC-011 | Alfonsonrx | 2026-09-24 | 2026-09-24 | Pendiente |

## Descripción
Los empleados solo deben ver y marcar sus propios registros; ver, editar y borrar registros de otros es exclusivo del administrador.

## Actor
Usuario / Usuario Administrador

## Precondiciones
- El usuario debe haber ingresado (JWT válido).

## Flujo normal
1. Empleado consulta su historial en `my-records`.
2. Administrador lista, edita o elimina cualquier registro.

## Flujo alterno
—

## Excepciones
- Empleado intenta listar todos, editar o borrar → `403`.

## Postcondiciones
Cada empleado solo accede a su información.

## Estado en el backend
- `AssistanceViewSet` usa `IsAuthenticated` para todo salvo `today-summary`: **cualquier autenticado puede listar, editar y borrar registros de todos**.

## Pendiente / criterios de aceptación
- [ ] `list`, `retrieve` de otros, `update`, `partial_update`, `destroy` → `IsAdminType` (extender `get_permissions` en `assistance/views.py`).
- [ ] `create` y `my-records` siguen abiertos a cualquier autenticado.
- [ ] Tests de permisos por acción.
- [ ] Actualizar `API.md`.
