from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.lecteur_list, name='member_list'),
    path('<int:pk>/', views.lecteur_detail, name='member_detail'),
    path('create/', views.LecteurCreateView.as_view(), name='member_create'),
    path('<int:pk>/update/', views.LecteurUpdateView.as_view(), name='member_update'),
    path('<int:pk>/delete/', views.LecteurDeleteView.as_view(), name='member_delete'),
]
