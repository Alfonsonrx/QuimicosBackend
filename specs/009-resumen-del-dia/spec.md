# 009 — Resumen del día

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| TEC-009 | Alfonsonrx | 2026-09-24 | 2026-09-24 | Hecho |

## Descripción
El administrador ve el estado de asistencia de hoy de todos los empleados activos y una tasa histórica de presencia por día de la semana.

## Actor
Usuario Administrador

## Precondiciones
- El usuario debe haber ingresado (JWT válido).
- El usuario debe ser tipo `administrador`.

## Flujo normal
1. El administrador abre el panel.
2. El sistema retorna conteos del día (`present`, `absence`, `anticipated_absence`), la lista por empleado y `weekly_rate` lun–vie.

## Flujo alterno
—

## Excepciones
- No admin → `403`.
- Sin token → `401`.

## Postcondiciones
El administrador visualiza el resumen del día.

## Estado en el backend
- `GET /assistance_api/assistances/today-summary/` → `AssistanceViewSet.today_summary`, `TodaySummarySerializer`.
- `weekly_rate` usa todo el historial; día sin datos = `null`. Detalle en `API.md`.
