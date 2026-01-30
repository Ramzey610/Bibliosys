#!/usr/bin/env python3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import Client
from django.urls import reverse
from members.models import Lecteur

c = Client()
print('login:', c.login(username='admin', password='admin123'))
url = reverse('members:member_create')
r = c.get(url)
print('GET status', r.status_code)

# Non-AJAX creation
email1 = 'testuser@example.com'
data = {
    'first_name': 'Test',
    'last_name': 'User',
    'email': email1,
    'phone': '',
    'address': '',
    'numero_abonnement': 'MEM-TEST-01',
    'statut': 'active',
    'is_active': True,
    'remarques': ''
}
r2 = c.post(url, data, follow=True)
print('POST status', r2.status_code)
# Utiliser get_messages pour récupérer correctement les messages stockés
from django.contrib.messages import get_messages
msgs = [m.message for m in get_messages(r2.wsgi_request)]
print('Messages via get_messages:', msgs)
print('Lecteur exists', Lecteur.objects.filter(email=email1).exists())
if Lecteur.objects.filter(email=email1).exists():
    l = Lecteur.objects.get(email=email1)
    print('Lecteur utilisateur:', l.utilisateur)
    print('Lecteur utilisateur username:', getattr(l.utilisateur, 'username', None))
    print('Lecteur utilisateur email:', getattr(l.utilisateur, 'email', None))

# AJAX quick add with provided password
c2 = Client()
print('ajax login:', c2.login(username='admin', password='admin123'))
email2 = 'ajax@example.com'
ajax_data = {
    'first_name': 'Ajax',
    'last_name': 'User',
    'email': email2,
    'phone': '',
    'numero_abonnement': '',
    'statut': 'active',
    'is_active': True,
    'user_password': 'S3cur3Passw0rd!',
    'user_confirm_password': 'S3cur3Passw0rd!'
}
resp = c2.post(url, ajax_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
print('AJAX status', resp.status_code)
try:
    print('AJAX json:', resp.json())
except Exception as e:
    print('AJAX resp not JSON', resp.content)

print('Final Lecteurs count:', Lecteur.objects.count())
print('Lecteur emails:', [l.email for l in Lecteur.objects.all()])
print('Done')
