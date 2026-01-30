"""
URL Configuration for Bibliotheque project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('library/', include('library.urls', namespace='library')),
    path('members/', include('members.urls')),
    path('loans/', include('loans.urls')),
    path('', include(('library.urls', 'library'), namespace='library-root')),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin customization
admin.site.site_header = "Gestion de Bibliothèque"
admin.site.site_title = "Admin Bibliothèque"
admin.site.index_title = "Bienvenue"
