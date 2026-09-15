# Configura el backend de RegistroAsistencia de punta a punta: entorno virtual,
# dependencias, archivo .env, migraciones y datos de ejemplo.
#
# Uso (PowerShell):
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#   (o habilita scripts una vez con: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned)
#
# Requisito previo: tener PostgreSQL corriendo con una base de datos
# llamada 'db_asistencias' (ver README.md).

$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

Write-Host "== Configurando RegistroAsistencia backend =="

$pythonBin = "python"
if (-not (Get-Command $pythonBin -ErrorAction SilentlyContinue)) {
    $pythonBin = "py"
}

if (-not (Test-Path "venv")) {
    Write-Host "-> Creando entorno virtual..."
    & $pythonBin -m venv venv
} else {
    Write-Host "-> Entorno virtual ya existe, se reutiliza."
}

& ".\venv\Scripts\Activate.ps1"

Write-Host "-> Instalando dependencias..."
pip install --upgrade pip | Out-Null
pip install -r requirements.txt

$envFile = "assistrecord\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "-> Generando $envFile con valores por defecto..."
    $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    @"
SECRET_KEY = '$secretKey'
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
"@ | Set-Content -Path $envFile -Encoding utf8
    Write-Host "   Revisa y ajusta DB_USER/DB_PASSWORD si tu Postgres local usa otras credenciales."
} else {
    Write-Host "-> $envFile ya existe, no se modifica."
}

Write-Host "-> Asegurate de tener la base de datos 'db_asistencias' creada en PostgreSQL antes de continuar."
Write-Host "-> Aplicando migraciones..."
python manage.py migrate

Write-Host "-> Cargando datos de ejemplo..."
python manage.py seed_demo_data

Write-Host ""
Write-Host "== Listo =="
Write-Host "Para trabajar en el proyecto, activa el entorno virtual y levanta el servidor:"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host "  python manage.py runserver"
