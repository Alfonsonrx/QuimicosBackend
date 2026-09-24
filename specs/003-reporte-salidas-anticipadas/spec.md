# 003 — Reporte de salidas anticipadas

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| RE-02 | GG | 01-01-2024 | 2026-09-24 | Pendiente |

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
- Los registros `type=salida` existen, pero no hay cálculo de salida anticipada ni endpoint.

## Pendiente / criterios de aceptación
- [ ] Criterio: registro `salida` con `time < 17:30`.
- [ ] Decidir si se guarda un flag (como `delay`) o se filtra al consultar; filtrar por `time` al consultar evita migración.
- [ ] Endpoint admin, p. ej. `GET /assistance_api/assistances/reports/early-exits/?from=&to=`, mismo formato que [002](../002-reporte-atrasos/spec.md).
- [ ] Tests: 17:30 exacto no es anticipada, 17:29 sí; empleado recibe `403`.
- [ ] Documentar en `API.md`.
