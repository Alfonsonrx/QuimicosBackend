# 013 — Horario laboral

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| TEC-013 | Alfonsonrx | 2026-09-25 | 2026-09-25 | Hecho |

## Descripción
El administrador define la hora de ingreso y de salida de la empresa. Se usan para marcar atrasos ([002](../002-reporte-atrasos/spec.md)) y salidas anticipadas ([003](../003-reporte-salidas-anticipadas/spec.md)).

## Actor
Usuario Administrador (edición); cualquier usuario (lectura)

## Precondiciones
- El usuario debe haber ingresado (JWT válido).
- Para editar, el usuario debe ser tipo `administrador`.

## Flujo normal
1. El administrador consulta el horario (`GET /assistance_api/schedule/`).
2. Cambia `entry_time` y/o `exit_time` (`PATCH`).
3. El sistema valida y guarda.
4. Las marcas nuevas usan el nuevo horario.

## Flujo alterno
—

## Excepciones
- `entry_time` ≥ `exit_time` → `400`.
- No admin intenta editar → `403`.

## Postcondiciones
El horario queda actualizado. Los registros ya guardados conservan sus `delay` / `early_exit`.

## Estado en el backend
- Modelo `WorkSchedule` (fila única, `WorkSchedule.get()`), defaults 09:30 / 17:30 (`assistance/models.py`).
- `WorkScheduleView` (`assistance/views.py`), `WorkScheduleSerializer` (`assistance/serialiser.py`), ruta en `assistance/urls.py`.
- Los flags se calculan al marcar en `schedule_flags`; cambiar el horario no reescribe el histórico.
- Tests en `assistance/tests.py`.
