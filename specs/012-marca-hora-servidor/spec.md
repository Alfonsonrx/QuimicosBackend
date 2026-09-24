# 012 — Marca con hora del servidor

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| TEC-012 | Alfonsonrx | 2026-09-24 | 2026-09-24 | Pendiente |

## Descripción
Al marcar entrada/salida, el sistema usa el usuario autenticado y la fecha/hora actual del servidor, como pide CA-01, en vez de confiar en lo que envía el cliente.

## Actor
Usuario

## Precondiciones
- El usuario debe haber ingresado (JWT válido).

## Flujo normal
1. El empleado envía solo `{"type": "ingreso"}` o `{"type": "salida"}`.
2. El sistema asigna `user=request.user`, `date`/`time` = `timezone.localtime()`.
3. El sistema calcula `delay` y confirma (`201`).

## Flujo alterno
El administrador puede seguir enviando `user`, `date` y `time` explícitos (p. ej. `falta_anticipada` o correcciones).

## Excepciones
- Empleado envía `user` de otra persona → se ignora o `403`.

## Postcondiciones
El registro refleja la hora real de la marca.

## Estado en el backend
- Hoy `AssistanceSerializer` exige `user`, `date` y `time` del cliente: un empleado puede marcar por otro o con cualquier hora.

## Pendiente / criterios de aceptación
- [ ] Para no-admin: `user`, `date`, `time` se ignoran y se toman del servidor.
- [ ] Para admin: se aceptan explícitos (mantiene [010](../010-falta-anticipada/spec.md)).
- [ ] Tests: empleado no puede marcar por otro ni fijar la hora.
- [ ] Actualizar `API.md` (input de `POST`).
