from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # L'inscription publique est désactivée (les comptes lecteurs sont créés par le bibliothécaire)
    # path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]
