# 004 — Reporte de inasistencias

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| RE-03 | GG | 01-01-2024 | 2026-09-27 | Hecho |

## Descripción
El Administrador puede elaborar un reporte de todos los que no registraron ni entrada ni salida en un día.

## Actor
Usuario Administrador

## Precondiciones
- El usuario debe haber ingresado (JWT válido).
- El usuario debe ser tipo `administrador`.

## Flujo normal
1. El usuario selecciona “reporte de inasistencias” (opcionalmente un rango de fechas).
2. El sistema retorna todos los días en que no se registraron entradas ni salidas, indicando el identificador de cada usuario.

## Flujo alterno
—

## Excepciones
- No admin → `403`.
- Rango de fechas inválido → `400`.

## Postcondiciones
El administrador puede visualizar el reporte de inasistencias.

## Estado en el backend
- Para el día actual también está `today-summary` (ver [009](../009-resumen-del-dia/spec.md)).
- `GET /assistance_api/assistances/reports/absences/` → `AssistanceViewSet.report_absences`: días hábiles sin ingreso ni salida, empleados activos, desde su `date_registered`; `falta_anticipada` → `justified: true`.
- Tests en `assistance/tests.py` (`ReportTests`).

## Criterios de aceptación
- [x] Endpoint admin, p. ej. `GET /assistance_api/assistances/reports/absences/?from=&to=`.
- [x] Considerar solo días hábiles (lun–vie) y usuarios activos tipo `empleado`.
- [x] Día sin `ingreso` ni `salida` = inasistencia; si tiene `falta_anticipada`, marcarla como justificada (ver [010](../010-falta-anticipada/spec.md)).
- [x] ~~Reutilizar la lógica de `today_summary`~~: no aplica, `today_summary` clasifica solo el día actual; el reporte recorre un rango con una consulta propia.
- [x] Tests: día sin registros aparece; fin de semana no; empleado recibe `403`.
- [x] Documentar en `API.md`.
