from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirection de la racine vers le dashboard
    path('', lambda request: redirect('dashboard:index')),
    
    # Apps
    path('auth/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('menu/', include('apps.menu.urls')),
    path('commandes/', include('apps.commandes.urls')),
    
    
    # Browser reload (dev)
    path('__reload__/', include('django_browser_reload.urls')),
]

# Media files en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)