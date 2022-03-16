#!/usr/bin/env bash

set -e

PROJECT_BASE_PATH='https://github.com/mostafa201272/crypto.git'

git pull
$PROJECT_BASE_PATH/env/bin/python manage.py migrate
$PROJECT_BASE_PATH/env/bin/python manage.py collectstatic --noinput
supervisorctl restart crypto

echo "DONE! :)"
