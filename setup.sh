#!/usr/bin/env bash
# Configura el backend de RegistroAsistencia de punta a punta: entorno virtual,
# dependencias, archivo .env, migraciones y datos de ejemplo.
#
# Uso:
#   ./setup.sh          (o: bash setup.sh)
#
# Requisito previo: tener PostgreSQL corriendo con una base de datos
# llamada 'db_asistencias' (ver README.md).
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "== Configurando RegistroAsistencia backend =="

PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" &> /dev/null; then
  PYTHON_BIN="python"
fi

if [ ! -d "venv" ]; then
  echo "-> Creando entorno virtual..."
  "$PYTHON_BIN" -m venv venv
else
  echo "-> Entorno virtual ya existe, se reutiliza."
fi

# shellcheck disable=SC1091
source venv/bin/activate

echo "-> Instalando dependencias..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt

ENV_FILE="assistrecord/.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "-> Generando ${ENV_FILE} con valores por defecto..."
  SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
  cat > "$ENV_FILE" <<EOF
SECRET_KEY = '${SECRET_KEY}'
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
EOF
  echo "   Revisa y ajusta DB_USER/DB_PASSWORD si tu Postgres local usa otras credenciales."
else
  echo "-> ${ENV_FILE} ya existe, no se modifica."
fi

echo "-> Asegurate de tener la base de datos 'db_asistencias' creada en PostgreSQL antes de continuar."
echo "-> Aplicando migraciones..."
python manage.py migrate

echo "-> Cargando datos de ejemplo..."
python manage.py seed_demo_data

echo ""
echo "== Listo =="
echo "Para trabajar en el proyecto, activa el entorno virtual y levanta el servidor:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
