# 014 — Reingreso autorizado

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| TEC-014 | Alfonsonrx | 2026-09-25 | 2026-09-25 | Hecho |

## Descripción
Si un empleado sale durante el día (p. ej. una hora) y vuelve, el administrador puede autorizar un nuevo ingreso. Se conserva todo el historial del día (ingreso 9:00, salida 13:00, ingreso 14:00, salida 18:00).

## Actor
Usuario Administrador (autoriza); Usuario (marca el reingreso)

## Precondiciones
- El administrador debe haber ingresado y ser tipo `administrador`.
- La última marca de hoy del empleado es `salida`.

## Flujo normal
1. El empleado marca `salida` (queda `early_exit=True` si es antes del horario).
2. El administrador autoriza el reingreso (`POST /assistance_api/assistances/allow-reentry/` con `{"user": id}`).
3. El `today-status` del empleado muestra `next: "ingreso"`.
4. El empleado marca `ingreso`; el permiso se consume.
5. Al terminar el día, el empleado marca `salida`.

## Flujo alterno
Si ya existe un permiso sin usar, se devuelve el mismo (`200`) en vez de crear otro.

## Excepciones
- El empleado no tiene una `salida` hoy → `400`.
- Usuario inexistente → `404`.
- No admin → `403`.
- Reingreso sin permiso, o un segundo reingreso con el mismo permiso → `400`.

## Postcondiciones
El empleado puede marcar un único ingreso adicional ese día. El reingreso nunca tiene `delay`.

## Estado en el backend
- Modelo `ReentryPermit` (`user`, `date`, `granted_by`, `used`) en `assistance/models.py`.
- `AssistanceViewSet.allow_reentry` (`assistance/views.py`); las reglas se aplican y el permiso se consume en `AssistanceSerializer.create`.
- La salida intermedia sigue siendo `early_exit`; el reporte [003](../003-reporte-salidas-anticipadas/spec.md) debe mirar la última salida del día.
- Tests en `assistance/tests.py` (`test_reentry_with_permit`).
