from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('', include('apps.menu.urls')),              # Page d'accueil = menu
    path('tables/', include('apps.restaurant.urls')),     # Gestion des tables
    path('cart/', include('apps.commandes.urls')),    # Panier et commandes
    path('paiements/', include('apps.paiements.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path("__reload__/", include("django_browser_reload.urls")),  # Hot reload Tailwind
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)