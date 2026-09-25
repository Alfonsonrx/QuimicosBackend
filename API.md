# RegistroAsistencia API

URL Base (dev): `http://localhost:8000`

Autenticacion: JWT (Libreria DRF Simplejwt). Se obtiene token a traves de /token/, para usar como header de autorizacion “Authorization: JWT <access_token>” en endpoints protegidos.

---

## Cambios (changelog)

Registro de cambios de la API para el frontend, mas reciente arriba. **breaking** = el frontend actual debe ajustarse. Las secciones afectadas llevan `🆕 (fecha)` en su titulo.

### 2026-09-25
- **breaking** — `POST /assistance_api/assistances/` ahora valida el orden de las marcas por usuario y dia: no se puede marcar `ingreso` dos veces seguidas, ni `salida` sin un `ingreso` abierto, ni volver a ingresar despues de una `salida` sin permiso del admin. Todos responden `400` con el error en `type`. Maximo una `falta_anticipada` por usuario y dia.
- **breaking** — `delay` ya no usa la hora fija 9:00: es `true` si el **primer** ingreso del dia es posterior a la hora de entrada configurada (9:30 por defecto). Una marca exactamente a las 9:30 no es atraso.
- Los registros de asistencia incluyen `name` (nombre completo), `position` y `early_exit` (salida antes de la hora de salida configurada, 17:30 por defecto). Todos de solo lectura.
- `PUT`/`PATCH /assistance_api/assistances/{id}/` recalculan `delay` y `early_exit` con el horario vigente.
- Nuevo `GET /assistance_api/assistances/today-status/`: marcas de hoy del usuario logueado y cual es la siguiente marca permitida (`next`), para habilitar el boton Entrada/Salida.
- Nuevo `POST /assistance_api/assistances/allow-reentry/` (admin): autoriza un reingreso hoy a un empleado que ya marco salida.
- Nuevo `GET` / `PATCH /assistance_api/schedule/`: horario de entrada/salida de la empresa (lectura cualquier autenticado, edicion solo admin).

### 2026-09-24
- Nuevo `/accounts_api/users/` (admin): listar, detalle, `PUT`/`PATCH`, `DELETE` (desactiva, no borra).
- Nuevo `GET /accounts_api/users/me/`: `id`, `name`, `first_lastname`, `type` del usuario logueado.
- **breaking** — `POST /accounts_api/registration/` responde `201` con el usuario creado (antes `{"message": "Registration successful."}`). Acepta `type`; crear un `administrador` exige `admin_password` (si no → `403`). La misma regla aplica al cambiar `type` a `administrador` en `PATCH /accounts_api/users/{id}/`.

---

## Autenticacion

### `POST /token/`
Obtener tokens de access/refresh. No protegido (No autenticacion requerida).

**Input**
```json
{
  "email": "jperez@example.com",
  "password": "MySecurePass123!"
}
```

**Output — 200**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Output — 401** (credenciales erroneas)
```json
{ "detail": "No active account found with the given credentials" }
```

### `POST /token/refresh/`
Refresca los token de acceso por unos nuevos.
(Solo 'access' son refrescados, refresh se mantienen activos)

**Input**
```json
{ "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

**Output — 200**
```json
{ "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

### `POST /token/verify/`
Verifica que un token es valido.

**Input**
```json
{ "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

**Output** — `200 {}` si es valido, `401` con un detalle del error si expiro o no es valido.

---

## Cuentas

### `POST /accounts_api/registration/`
Registra nuevo usuario, requiere token de acceso y que el usuario sea un administrador. Los nuevos usuario tienen `is_active=True` y `type="empleado"` por defecto; no hay metodo de activacion por correo al ser todo local.

**Input**
```json
{
  "email": "jperez@example.com",
  "password": "MySecurePass123!",
  "re_password": "MySecurePass123!",
  "name": "Juan",
  "first_lastname": "Perez",
  "type": "empleado"
}
```
- `type` es opcional (`empleado` por defecto) y acepta `empleado` o `administrador`.
- Para crear un `administrador` se debe enviar ademas `admin_password`: la contraseña **del administrador que hace la peticion**. Se verifica contra su usuario; si falta o no coincide → `403` y no se crea nada.

**Output — 201** (mismo formato que `GET /accounts_api/users/{id}/`)
```json
{
  "id": 7,
  "email": "jperez@example.com",
  "name": "Juan",
  "first_lastname": "Perez",
  "second_lastname": null,
  "type": "empleado",
  "phone": null,
  "position": null,
  "is_active": true,
  "date_registered": "2026-09-24T12:00:00Z"
}
```

**Output — 400** (contraseñas no coinciden, contraseña debil, email duplicado) 
```json
{ "re_password": ["Passwords do not match."] }
```
o
```json
{ "email": ["user with this Email already exists."] }
```

**Output — 403** (`type: "administrador"` sin `admin_password` valido)
```json
{ "detail": "admin_password is required and must match your password to grant administrador." }
```

### `GET /accounts_api/users/me/`
Datos básicos del usuario autenticado (cualquier tipo), pensados para guardarse en el frontend al iniciar sesión. Solo lectura.

**Output — 200**
```json
{
  "id": 3,
  "name": "Juan",
  "first_lastname": "Perez",
  "type": "empleado"
}
```

### `/accounts_api/users/` (solo administradores)
El alta de usuarios sigue en `registration/`. Un empleado recibe `403`.

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/accounts_api/users/` | Lista paginada (`?limit=&offset=`) |
| GET | `/accounts_api/users/{id}/` | Detalle |
| PUT / PATCH | `/accounts_api/users/{id}/` | Edita `email`, `name`, `first_lastname`, `second_lastname`, `type`, `phone`, `position`, `is_active` |
| DELETE | `/accounts_api/users/{id}/` | Desactiva (`is_active=false`), no borra; conserva el historial de asistencias. `204` |

Para reactivar: `PATCH {"is_active": true}`.

Ascender a un usuario a `administrador` (`type: "administrador"` en `PUT`/`PATCH`) exige `admin_password`, igual que en `registration/`; si falta o no coincide → `403`. Editar otros campos de un usuario que ya es administrador no lo pide.

**Output de detalle — 200**
```json
{
  "id": 3,
  "email": "jperez@example.com",
  "name": "Juan",
  "first_lastname": "Perez",
  "second_lastname": null,
  "type": "empleado",
  "phone": null,
  "position": null,
  "is_active": true,
  "date_registered": "2026-09-24T12:00:00Z"
}
```

---

## Registros de asistencia

Endpoint Base: `/assistance_api/assistances/`. Todas las acciones requieren autenticacion: `Authorization: JWT <access_token>` (`IsAuthenticated`), excepto `today-summary` y `allow-reentry` que adicionalmente requieren que el usuario sea tipo `administrador`.

Todos los registros se devuelven con este formato. `name`, `position`, `delay` y `early_exit` son de solo lectura:
```json
{
  "id": 1,
  "date": "2026-09-14",
  "time": "08:05:00",
  "type": "ingreso",
  "user": 3,
  "name": "Juan Perez Diaz",
  "position": "Bodeguero",
  "delay": false,
  "early_exit": false
}
```

El `type` de un registro puede ser:
- `ingreso` — marca de entrada
- `salida` — marca de salida
- `falta_anticipada` 🆕 — una falta anticipada pre-registrada por un admin a nombre de un empleado

### `GET /assistance_api/assistances/` 🆕 (2026-09-25)
Lista los registros (paginado — `LimitOffsetPagination`, tamaño de pagina por defecto 50). Cualquier usuario autenticado (actualmente sin filtrar — todos ven los registros de todos los usuarios).

**Output — 200**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "date": "2026-09-14",
      "time": "08:05:00",
      "type": "ingreso",
      "user": 3,
      "name": "Juan Perez Diaz",
      "position": "Bodeguero",
      "delay": false,
      "early_exit": false
    },
    {
      "id": 2,
      "date": "2026-09-14",
      "time": "17:30:00",
      "type": "salida",
      "user": 3,
      "name": "Juan Perez Diaz",
      "position": "Bodeguero",
      "delay": false,
      "early_exit": false
    }
  ]
}
```

### `POST /assistance_api/assistances/` 🆕 (2026-09-25)
Crea un registro.

**Input**
```json
{
  "user": 3,
  "type": "ingreso",
  "date": "2026-09-14",
  "time": "09:15:00"
}
```

- `delay` es **de solo lectura**. Se calcula al marcar: `true` solo si es el **primer** `ingreso` del dia y `time` es posterior a `entry_time` del horario (9:30 por defecto; 9:30 exacto no es atraso). Un reingreso nunca tiene `delay`.
- `early_exit` es **de solo lectura**. `true` si `type` es `salida` y `time` es anterior a `exit_time` (17:30 por defecto; 17:30 exacto no es anticipada). Una salida intermedia (antes de un reingreso) tambien queda con `early_exit: true`.
- Cambiar el horario **no** modifica registros ya guardados.

**Reglas de marcado** (por usuario y fecha; aplican a todo `POST`, incluso de un admin):
- `ingreso`: permitido si no hay marcas ese dia, o si la ultima es `salida` **y** el admin dio permiso de reingreso (`allow-reentry`). Cada permiso sirve para un solo reingreso.
- `salida`: permitida solo si la ultima marca es `ingreso`.
- `falta_anticipada`: no participa del orden; maximo una por dia.
- Si no se cumple → `400`:
```json
{ "type": ["An ingreso is already open for this user on this date."] }
```
```json
{ "type": ["There is no open ingreso to close with a salida."] }
```
```json
{ "type": ["Re-entry requires an administrador authorization."] }
```
```json
{ "type": ["An anticipated absence already exists for this user on this date."] }
```
- `type: "falta_anticipada"` 🆕 solo puede ser enviado por un usuario tipo `administrador` (se valida en el serializer, no en un permission de la vista) — si un empleado intenta enviar este tipo recibe un `400`, no un `403`.

**Output — 201** (primer ingreso despues de la hora de entrada)
```json
{
  "id": 5,
  "date": "2026-09-14",
  "time": "09:40:00",
  "type": "ingreso",
  "user": 3,
  "name": "Juan Perez Diaz",
  "position": "Bodeguero",
  "delay": true,
  "early_exit": false
}
```

**Output — 201** (admin registrando una falta anticipada para el empleado `4`)
```json
{
  "id": 6,
  "date": "2026-09-15",
  "time": "00:00:00",
  "type": "falta_anticipada",
  "user": 4,
  "name": "Maria Lopez",
  "position": "Analista",
  "delay": false,
  "early_exit": false
}
```

**Output — 400** (un usuario no-admin intenta enviar `falta_anticipada`)
```json
{ "type": ["Only administrador-type users can register an anticipated absence."] }
```

### `GET /assistance_api/assistances/{id}/`
Obtiene un solo registro. Mismo formato que un elemento de la lista de arriba.

### `PUT` / `PATCH /assistance_api/assistances/{id}/` 🆕 (2026-09-25)
Actualiza un registro (correcciones). No aplica las reglas de marcado. `delay` y `early_exit` se recalculan con el horario vigente.

### `DELETE /assistance_api/assistances/{id}/`
Elimina un registro. **204** en caso de exito.

### `GET /assistance_api/assistances/my-records/`
Retorna solo los registros del usuario que hace la peticion (paginado, mismo formato que el endpoint de lista). Cualquier usuario autenticado.

**Output — 200**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "date": "2026-09-14", "time": "08:05:00", "type": "ingreso", "user": 3, "name": "Juan Perez Diaz", "position": "Bodeguero", "delay": false, "early_exit": false }
  ]
}
```

### `GET /assistance_api/assistances/today-status/` 🆕 (2026-09-25)
Estado de hoy del usuario logueado (cualquier tipo). Sirve para saber si ya marco y que boton habilitar.

**Output — 200**
```json
{
  "ingreso": "09:02:00",
  "salida": null,
  "next": "salida",
  "records": [
    { "id": 10, "date": "2026-09-25", "time": "09:02:00", "type": "ingreso", "user": 3, "name": "Juan Perez Diaz", "position": "Bodeguero", "delay": false, "early_exit": false }
  ]
}
```
- `ingreso`: hora del primer ingreso de hoy, o `null`.
- `salida`: hora de la ultima salida de hoy, o `null`.
- `next`: la siguiente marca permitida: `"ingreso"`, `"salida"` o `null`. `null` significa que ya salio y no tiene permiso de reingreso.
- `records`: todas las marcas de hoy (incluye `falta_anticipada`), ordenadas por hora.

### `POST /assistance_api/assistances/allow-reentry/` 🆕 (2026-09-25)
Solo admin. Autoriza **un** reingreso hoy a un empleado cuya ultima marca de hoy es `salida` (p. ej. salio una hora y volvio).

**Input**
```json
{ "user": 3 }
```

**Output — 201** (permiso creado) o **200** (ya habia uno sin usar, se devuelve el mismo)
```json
{ "id": 1, "user": 3, "date": "2026-09-25", "used": false }
```

**Output — 400** (el empleado no tiene una salida hoy)
```json
{ "user": ["User has no salida today to re-enter from."] }
```
`404` si el usuario no existe; `403` si quien llama no es admin.

### `GET` / `PATCH /assistance_api/schedule/` 🆕 (2026-09-25)
Horario de la empresa, uno solo para todos. `GET` para cualquier autenticado; `PATCH` solo admin (`403` si no).

**Output — 200**
```json
{ "entry_time": "09:30:00", "exit_time": "17:30:00" }
```

**Input `PATCH`** (parcial)
```json
{ "entry_time": "09:00" }
```

**Output — 400** (entrada no es anterior a la salida)
```json
{ "exit_time": ["exit_time must be later than entry_time."] }
```
Solo afecta a las marcas nuevas; el historico conserva sus `delay` / `early_exit`.

### `GET /assistance_api/assistances/today-summary/` 🆕
Solo admin (`IsAuthenticated` + tipo `administrador`). Resume la asistencia del dia y una tasa historica de asistencia por dia de la semana, para todos los usuarios activos de tipo `empleado`.

**Output — 200**
```json
{
  "todays_records": {
    "present": 8,
    "absence": 1,
    "anticipated_absence": 2
  },
  "today_list": [
    { "name": "Juan Perez", "position": "Bodeguero", "record_type": "present" },
    { "name": "Maria Lopez", "position": "Analista", "record_type": "anticipated_absence" },
    { "name": "Carlos Ruiz", "position": null, "record_type": "absence" }
  ],
  "weekly_rate": {
    "monday": 92.5,
    "tuesday": 88.0,
    "wednesday": null,
    "thursday": 100.0,
    "friday": 95.0
  }
}
```
Los porcentajes de `weekly_rate` se calculan sobre **todos los datos historicos** para cada dia de la semana (no solo la semana actual); un dia sin ningun registro historico vuelve como `null` en vez de `0`. El `record_type` de cada elemento de `today_list` usa los mismos tres valores que las claves de `todays_records`: `present`, `absence`, `anticipated_absence`.

**Output — 403** (autenticado pero no es tipo admin)
```json
{ "detail": "Only administrador-type users may access this resource." }
```

**Output — 401** (sin token o token invalido)
```json
{ "detail": "Authentication credentials were not provided." }
```

---

## Problemas conocidos (no forman parte del contrato de esta API)

- El admin de Django (`/admin/`) es exclusivo para superusuarios en este proyecto — **no** es donde los usuarios tipo `administrador` gestionan datos. Todo lo que necesitan esta expuesto a traves de la API de arriba, protegido con una validacion de tipo admin.
