# RegistroAsistencia API

URL Base (dev): `http://localhost:8000`

Autenticacion: JWT (Libreria DRF Simplejwt). Se obtiene token a traves de /token/, para usar como header de autorizacion “Authorization: JWT <access_token>” en endpoints protegidos.

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

Endpoint Base: `/assistance_api/assistances/`. Todas las acciones requieren autenticacion: `Authorization: JWT <access_token>` (`IsAuthenticated`), excepto `today-summary` que adicionalmente requiere que el usuario sea tipo `administrador`.

El `type` de un registro puede ser:
- `ingreso` — marca de entrada
- `salida` — marca de salida
- `falta_anticipada` 🆕 — una falta anticipada pre-registrada por un admin a nombre de un empleado

### `GET /assistance_api/assistances/`
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
      "delay": false
    },
    {
      "id": 2,
      "date": "2026-09-14",
      "time": "17:30:00",
      "type": "salida",
      "user": 3,
      "delay": false
    }
  ]
}
```

### `POST /assistance_api/assistances/`
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

- `delay` 🆕 es **de solo lectura** — nunca se envia. Se calcula del lado del servidor solo cuando `type` es `"ingreso"`: `true` si `time` es igual o posterior a una hora de corte hardcodeada (actualmente 9:00), `false` en cualquier otro caso (incluyendo `salida`/`falta_anticipada`).
- `type: "falta_anticipada"` 🆕 solo puede ser enviado por un usuario tipo `administrador` (se valida en el serializer, no en un permission de la vista) — si un empleado intenta enviar este tipo recibe un `400`, no un `403`.

**Output — 201** (ingreso enviado a la hora de corte o despues)
```json
{
  "id": 5,
  "date": "2026-09-14",
  "time": "09:20:00",
  "type": "ingreso",
  "user": 3,
  "delay": true
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
  "delay": false
}
```

**Output — 400** (un usuario no-admin intenta enviar `falta_anticipada`)
```json
{ "type": ["Only administrador-type users can register an anticipated absence."] }
```

### `GET /assistance_api/assistances/{id}/`
Obtiene un solo registro. Mismo formato que un elemento de la lista de arriba.

### `PUT` / `PATCH /assistance_api/assistances/{id}/`
Actualiza un registro. `delay` no se vuelve a calcular al actualizar — solo cambia al crear un registro nuevo con `POST`.

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
    { "id": 1, "date": "2026-09-14", "time": "08:05:00", "type": "ingreso", "user": 3, "delay": false }
  ]
}
```

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
