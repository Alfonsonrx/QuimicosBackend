# 003 — Reporte de salidas anticipadas

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| RE-02 | GG | 01-01-2024 | 2026-09-25 | Pendiente |

## Descripción
El Administrador puede elaborar un reporte de todos los que salen antes de las 17:30, lo que se considera una “salida anticipada”.

## Actor
Usuario Administrador

## Precondiciones
- El usuario debe haber ingresado (JWT válido).
- El usuario debe ser tipo `administrador`.

## Flujo normal
1. El usuario selecciona “reporte de salidas anticipadas” (opcionalmente un rango de fechas).
2. El sistema retorna todas las salidas antes de las 17:30, indicando el identificador de cada usuario y los días que salió anticipadamente.

## Flujo alterno
—

## Excepciones
- No admin → `403`.
- Rango de fechas inválido → `400`.

## Postcondiciones
El administrador puede visualizar el reporte de salidas anticipadas.

## Estado en el backend
- `AssistanceRecord.early_exit` se guarda al marcar: `salida` anterior a `WorkSchedule.exit_time` (17:30 por defecto, configurable, ver [013](../013-horario-laboral/spec.md)); se recalcula en `PUT/PATCH`.
- Una salida intermedia antes de un reingreso ([014](../014-reingreso/spec.md)) también queda `early_exit=True`.
- No existe endpoint de reporte.

## Pendiente / criterios de aceptación
- [x] Criterio: `salida` con `time < exit_time` (flag `early_exit`, guardado al marcar para no reescribir el histórico).
- [ ] El reporte considera solo la **última** salida de cada día (si el empleado volvió, la salida intermedia no cuenta).
- [ ] Endpoint admin, p. ej. `GET /assistance_api/assistances/reports/early-exits/?from=&to=`, mismo formato que [002](../002-reporte-atrasos/spec.md).
- [x] Tests de umbral (17:30 no, 17:29 sí) en `assistance/tests.py`.
- [ ] Test del endpoint: empleado recibe `403`.
- [ ] Documentar en `API.md`.
