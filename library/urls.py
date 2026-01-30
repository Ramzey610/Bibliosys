from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/create/', views.BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]
