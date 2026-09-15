# RegistroAsistencia — Backend

## Utilizacion de este backend

Para mas informacion sobre los endpoints disponibles, ver [API.md](API.md).

Se recomienda usar [Postman](https://www.postman.com/) para probar los endpoints manualmente.

## Puesta en marcha

### 1. Clonar el repositorio

```
git clone https://github.com/Alfonsonrx/QuimicosBackend.git
```

### 2. Base de datos

Antes que nada, es necesario contar con una base de datos **PostgreSQL 15** (la version mas estable y soportada a la fecha) con el nombre `db_asistencias`. Este paso no lo automatiza el script de configuracion (ver mas abajo): cada quien puede tener Postgres instalado de forma distinta (local, Docker, etc.), asi que hay que crear la base de datos a mano antes de continuar.

### 3. Configuracion automatica (recomendado)

Una vez creada la base de datos, se puede automatizar todo lo que sigue (entorno virtual, dependencias, archivo `.env` y migraciones) con un solo script.

En Linux/macOS:

```
./setup.sh
```

En Windows (PowerShell):

```
powershell -ExecutionPolicy Bypass -File setup.ps1
```

(Si PowerShell bloquea la ejecucion de scripts, basta con habilitarlo una vez por usuario: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.)

El script es seguro de volver a ejecutar: si el entorno virtual o el `.env` ya existen, los reutiliza en vez de sobreescribirlos. Al terminar, deja el proyecto listo salvo por el ultimo paso (levantar el servidor, ver seccion 4).

Los pasos 3.1 a 3.3 de abajo explican en detalle que hace el script, por si se prefiere ejecutarlos a mano o el script falla en algun punto.

### 3.1. Entorno virtual de Python (manual)

Para trabajar en el proyecto de forma aislada, se recomienda usar un entorno virtual. Dentro de la carpeta del repositorio, ejecutar:

```
python -m venv venv
```

Luego activarlo. En Windows:

```
.\venv\Scripts\activate.bat
```

En Linux/macOS:

```
source venv/bin/activate
```

Con el entorno activado, instalar las dependencias del proyecto (listadas en `requirements.txt`):

```
pip install -r requirements.txt
```

Esperar a que termine la instalacion antes de continuar.

### 3.2. Archivo `.env` (manual)

Dentro de la carpeta `assistrecord` es necesario crear un archivo `.env` con las siguientes variables:

```ini
SECRET_KEY = '<django_secret_key>'
ALLOWED_HOSTS = 'localhost'
DOMAIN = 'localhost'
SITE_NAME = 'localhost'

TENANT_BASE_DOMAIN='localhost'
FRONTEND_PROTOCOL='http'
FRONTEND_URL='localhost:5173'
# REDIS_URL='redis://127.0.0.1:6379/1'
LOG_PATH="./logfile.log"
DB_NAME = 'db_asistencias'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_USER = 'postgres'
DB_PASSWORD = ''

# Development only. Defaults to False in settings.py so unconfigured
# deploys fail closed; local dev opts in explicitly.
DEBUG=True
```

Para generar el `SECRET_KEY`, ejecutar:

```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Esto entrega una clave similar a:

```
^z$k4tsff18r&q)ckoq4@jwe_%2ys)^%w)z7gt=^wfm=&9y+by
```

Esa clave debe copiarse en `<django_secret_key>`.

### 3.3. Migraciones y datos de ejemplo (manual)

Django usa un ORM: las clases definidas en cada `models.py` son la plantilla de las tablas que se crean en la base de datos. Para crear esas tablas, ejecutar:

```
python manage.py migrate
```

Opcionalmente, para probar el sistema con datos de ejemplo, existe un comando que llena la base de datos con usuarios y registros de asistencia ficticios:

```
python manage.py seed_demo_data
```

### 4. Levantar el backend

Con todo lo anterior listo, el backend puede iniciarse con:

```
python manage.py runserver
```
