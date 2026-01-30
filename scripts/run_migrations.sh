#!/usr/bin/env bash
# Script d'aide pour exécuter les migrations sur une machine de confiance (CI ou local)
# Usage : DATABASE_URL="postgres://user:pass@host:5432/db" ./scripts/run_migrations.sh
set -euo pipefail

# Vérification minimale
if [ -z "${DATABASE_URL:-}" ]; then
  echo "Erreur: la variable d'environnement DATABASE_URL doit être définie avant d'exécuter ce script."
  echo "Exemple : DATABASE_URL=\"postgres://user:pass@host:5432/dbname\" $0"
  exit 2
fi

echo "Utilisation de DATABASE_URL = (masqué)"
export DJANGO_SETTINGS_MODULE=config.settings

# Installer les dépendances si nécessaire
if [ ! -d ".venv" ]; then
  echo "Virtualenv not found. On suppose que vous avez un environnement Python actif."
fi

# Exécuter les migrations
python manage.py migrate --noinput

echo "Migrations exécutées avec succès."