# 001 — Control de asistencia

| ID | Autor | Creación | Actualización | Estado |
|---|---|---|---|---|
| CA-01 | GG | 01-01-2024 | 2026-09-24 | Parcial |

## Descripción
La aplicación debe permitir el control de asistencia de los empleados. Los usuarios entran con correo y contraseña y marcan su entrada y su salida con un botón.

## Actor
Usuario

## Precondiciones
- Los usuarios deben estar creados.
- Los usuarios deben haber ingresado mediante login (`POST /token/` con email y contraseña).

## Flujo normal
1. Usuario presiona botón Entrada/Salida.
2. El sistema almacena el identificador del usuario, la acción (`ingreso`/`salida`), la fecha y hora actual.
3. El sistema confirma el registro (`201`).
4. Usuario presiona Cerrar sesión.

## Flujo alterno
Usuario presiona Cerrar sesión sin marcar Entrada/Salida.

## Excepciones
- Token inválido o expirado → `401`.

## Postcondiciones
El sistema presenta la ventana de Login.

## Estado en el backend
- Login: `POST /token/` (simplejwt, `USERNAME_FIELD = email`).
- Marca: `POST /assistance_api/assistances/` (`assistance/views.py` → `AssistanceViewSet`, `assistance/serialiser.py` → `AssistanceSerializer`).
- Historial propio: `GET /assistance_api/assistances/my-records/`.
- **Brecha:** el cliente envía `user`, `date` y `time`; el sistema no toma la fecha/hora actual por sí mismo. Ver [012](../012-marca-hora-servidor/spec.md).

## Pendiente / criterios de aceptación
- [ ] Resolver [012-marca-hora-servidor](../012-marca-hora-servidor/spec.md).
