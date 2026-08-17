#!/usr/bin/env bash
set -euo pipefail

echo "-> Instalando dependencias Python"
pip install -r requirements.txt

echo "-> Construyendo Tailwind CSS"
npm ci
npm run build

echo "-> Recopilando estáticos"
python manage.py collectstatic --noinput

echo "-> Aplicando migraciones"
python manage.py migrate --noinput

echo "-> Build completado"