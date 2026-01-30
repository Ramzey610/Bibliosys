from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.loan_list, name='loan_list'),
    path('<int:pk>/', views.loan_detail, name='loan_detail'),

    # Demandes d'emprunt (lecteur -> bibliothécaire)
    path('demande/', views.demande_emprunt, name='demande_emprunt'),
    path('demandes/', views.liste_demandes_emprunt, name='liste_demandes_emprunt'),
    path('demandes/<int:pk>/<str:decision>/', views.valider_demande_emprunt, name='valider_demande_emprunt'),

    # Demandes de retour (lecteur -> bibliothécaire)
    path('demande-retour/', views.demande_retour, name='demande_retour'),
    path('demandes-retour/', views.liste_demandes_retour, name='liste_demandes_retour'),
    path('demandes-retour/<int:pk>/<str:decision>/', views.valider_demande_retour, name='valider_demande_retour'),

    path('my-loans/', views.my_loans, name='my_loans'),
    path('history/', views.loan_history, name='loan_history'),
]
