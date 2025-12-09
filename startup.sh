#!/bin/bash

echo "Instalando dependencias desde requirements.txt..."
pip install --upgrade pip
pip install -r /home/site/wwwroot/requirements.txt

echo "Iniciando servidor gunicorn..."
python /home/site/wwwroot/manage.py collectstatic --noinput
gunicorn --bind=0.0.0.0:8000 proyect.wsgi:application
#az webapp log tail --name NewHope --resource-group Begginer