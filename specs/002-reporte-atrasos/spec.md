# 002 — Reporte de atrasos

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| RE-01 | GG | 01-01-2024 | 2026-09-25 | Pendiente |

## Descripción
El Administrador puede elaborar un reporte de todos los que entran después de las 9:30, lo que se considera una “entrada atrasada”.

## Actor
Usuario Administrador

## Precondiciones
- El usuario debe haber ingresado (JWT válido).
- El usuario debe ser tipo `administrador`.

## Flujo normal
1. El usuario selecciona “reporte de entradas atrasadas” (opcionalmente un rango de fechas).
2. El sistema retorna todas las entradas posteriores a 9:30, indicando el identificador de cada usuario y los días que llegó atrasado.

## Flujo alterno
—

## Excepciones
- No admin → `403`.
- Rango de fechas inválido → `400`.

## Postcondiciones
El administrador puede visualizar el reporte de atrasos.

## Estado en el backend
- `AssistanceRecord.delay` se calcula al marcar (`schedule_flags` en `assistance/serialiser.py`): primer `ingreso` del día posterior a `WorkSchedule.entry_time` (9:30 por defecto, configurable, ver [013](../013-horario-laboral/spec.md)).
- `delay` se recalcula en `PUT/PATCH`.
- No existe endpoint de reporte.

## Pendiente / criterios de aceptación
- [x] Umbral de atraso = 9:30, configurable (entrada estrictamente posterior es atraso).
- [x] Recalcular `delay` también al editar `time`/`type` de un registro.
- [ ] Endpoint admin (filtrar `delay=True`), p. ej. `GET /assistance_api/assistances/reports/late/?from=YYYY-MM-DD&to=YYYY-MM-DD`.
- [ ] Respuesta agrupada por usuario: id, nombre, lista de días con hora de entrada.
- [x] Tests de umbral (9:30 no, 9:31 sí) en `assistance/tests.py`.
- [ ] Test del endpoint: empleado recibe `403`.
- [ ] Documentar en `API.md`.
