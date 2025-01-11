from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("api.urls")),
]

print('DEBUG: ', settings.DEBUG)
if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

print(urlpatterns)