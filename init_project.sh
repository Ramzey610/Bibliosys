#!/bin/bash
# Script de démarrage du projet Bibliothèque

echo "🚀 Initialisation du projet Bibliothèque Django..."
echo ""

# Activer l'environnement virtuel si nécessaire
if [ -d "venv" ]; then
    echo "✓ Environnement virtuel détecté"
    source venv/bin/activate
fi

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -q -r requirements.txt

# Créer les migrations
echo "🔄 Création des migrations..."
python manage.py makemigrations 2>/dev/null || true

# Appliquer les migrations
echo "💾 Application des migrations..."
python manage.py migrate --quiet

# Créer le superutilisateur
echo ""
echo "👤 Création d'un utilisateur administrateur"
echo "   Username: admin"
echo "   Password: admin123"
echo "   Email: admin@bibliotheque.local"
echo ""
python manage.py shell << END
from accounts.models import CustomUser
if not CustomUser.objects.filter(username='admin').exists():
    CustomUser.objects.create_superuser(
        username='admin',
        email='admin@bibliotheque.local',
        password='admin123',
        first_name='Admin',
        last_name='Système',
        role='admin',
        is_librarian=True
    )
    print("✅ Utilisateur admin créé")
else:
    print("⚠️  Utilisateur admin déjà existant")
END

# Charger les données de test
echo ""
echo "📚 Chargement des données de test..."
python manage.py load_test_data

echo ""
echo "✅ Initialisation terminée!"
echo ""
echo "🌐 Pour démarrer le serveur, utilisez:"
echo "   python manage.py runserver"
echo ""
echo "📊 Accédez à:"
echo "   - Dashboard admin interne: http://localhost:8000/ (interface Django `/admin/` accessible aux superusers)"
echo ""
echo "👤 Comptes de test:"
echo "   - Admin: admin / admin123"
echo "   - Lecteur: lecteur / lecteur123"
echo ""
