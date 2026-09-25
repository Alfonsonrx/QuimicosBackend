# 001 — Control de asistencia

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| CA-01 | GG | 01-01-2024 | 2026-09-25 | Parcial |

## Descripción
La aplicación debe permitir el control de asistencia de los empleados. Los usuarios entran con correo y contraseña y marcan su entrada y su salida con un botón.

## Actor
Usuario

## Precondiciones
- Los usuarios deben estar creados.
- Los usuarios deben haber ingresado mediante login (`POST /token/` con email y contraseña).

## Flujo normal
1. El frontend consulta `today-status` y habilita el botón según `next`.
2. Usuario presiona botón Entrada/Salida.
3. El sistema valida el orden de marcas y almacena el identificador del usuario, la acción (`ingreso`/`salida`), la fecha y hora actual.
4. El sistema confirma el registro (`201`) con nombre y cargo del usuario.
5. Usuario presiona Cerrar sesión.

## Flujo alterno
- Usuario presiona Cerrar sesión sin marcar Entrada/Salida.
- El usuario sale durante el día y vuelve: el administrador le da permiso de reingreso y el usuario marca un nuevo ingreso (ver [014](../014-reingreso/spec.md)).

## Excepciones
- Token inválido o expirado → `401`.
- Doble `ingreso`, `salida` sin ingreso abierto, o reingreso sin permiso → `400`.

## Postcondiciones
El sistema presenta la ventana de Login.

## Estado en el backend
- Login: `POST /token/` (simplejwt, `USERNAME_FIELD = email`).
- Marca: `POST /assistance_api/assistances/` (`assistance/views.py` → `AssistanceViewSet`, `assistance/serialiser.py` → `AssistanceSerializer`).
- Historial propio: `GET /assistance_api/assistances/my-records/`.
- Estado de hoy: `GET /assistance_api/assistances/today-status/` → `ingreso`, `salida`, `next`, `records`.
- Los registros incluyen `name` (`User.full_name`) y `position`.
- Reglas de marcado en `AssistanceSerializer.create`: las marcas alternan ingreso/salida por usuario y día, dentro de una transacción con bloqueo de la fila del usuario, así que dos requests simultáneas no pueden duplicar una marca.
- **Brecha:** el cliente envía `user`, `date` y `time`; el sistema no toma la fecha/hora actual por sí mismo. Ver [012](../012-marca-hora-servidor/spec.md).

## Pendiente / criterios de aceptación
- [ ] Resolver [012-marca-hora-servidor](../012-marca-hora-servidor/spec.md).
