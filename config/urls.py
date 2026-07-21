from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Em produção (Railway) não há servidor separado para arquivos de media
    # (whitenoise só cobre STATIC_ROOT). Servimos /media/ via Django mesmo
    # fora do DEBUG para que avatares enviados pelos usuários funcionem.
    # Observação: o filesystem do Railway é efêmero sem um Volume montado em
    # MEDIA_ROOT — sem volume, avatares enviados são perdidos a cada deploy.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)