# 010 — Falta anticipada

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| TEC-010 | Alfonsonrx | 2026-09-24 | 2026-09-24 | Hecho |

## Descripción
El administrador pre-registra una ausencia justificada a nombre de un empleado.

## Actor
Usuario Administrador

## Precondiciones
- El usuario debe haber ingresado (JWT válido).
- El usuario debe ser tipo `administrador`.

## Flujo normal
1. El administrador crea un registro `type=falta_anticipada` para un usuario y fecha.
2. El sistema lo guarda (`201`).

## Flujo alterno
—

## Excepciones
- Un no-admin que envía `falta_anticipada` → `400` (validado en el serializer, no en permisos).

## Postcondiciones
El día del empleado cuenta como `anticipated_absence` en el resumen.

## Estado en el backend
- `POST /assistance_api/assistances/` con `type=falta_anticipada`; validación en `AssistanceSerializer.validate`.
- Usada por [009](../009-resumen-del-dia/spec.md); debe usarse en [004](../004-reporte-inasistencias/spec.md).
