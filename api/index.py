"""
Point d'entrée serverless pour Vercel.
Utilise `vercel-wsgi` pour exposer l'application WSGI Django au runtime Vercel (@vercel/python).

Noms et commentaires en FRANÇAIS pour contexte pédagogique.
"""
import os

# Définir les settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Charger l'application WSGI Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Adapter l'application WSGI au handler attendu par Vercel
# Le package `vercel-wsgi` expose `make_handler` pour cela.
try:
    from vercel_wsgi import make_handler
    handler = make_handler(application)
except Exception:
    # Si `vercel-wsgi` n'est pas disponible (en local), exposer `application` pour tests
    handler = application
