#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Seed database with test data (only if empty)
echo "Checking if database needs seeding..."
python manage.py seed_data --users 10 --posts 20
