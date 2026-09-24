# 004 — Reporte de inasistencias

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| RE-03 | GG | 01-01-2024 | 2026-09-24 | Parcial |

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
- `GET /assistance_api/assistances/today-summary/` ya clasifica a cada empleado activo **solo para hoy** en `present`, `absence`, `anticipated_absence` (ver [009](../009-resumen-del-dia/spec.md)).
- No hay reporte por rango ni por usuario/día.

## Pendiente / criterios de aceptación
- [ ] Endpoint admin, p. ej. `GET /assistance_api/assistances/reports/absences/?from=&to=`.
- [ ] Considerar solo días hábiles (lun–vie) y usuarios activos tipo `empleado`.
- [ ] Día sin `ingreso` ni `salida` = inasistencia; si tiene `falta_anticipada`, marcarla como justificada (ver [010](../010-falta-anticipada/spec.md)).
- [ ] Reutilizar la lógica de `today_summary` en `assistance/views.py` en vez de duplicarla.
- [ ] Tests: día sin registros aparece; fin de semana no; empleado recibe `403`.
- [ ] Documentar en `API.md`.
