
#  imports libraries
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# creates main app urlpatterns list
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# defines urlpatterns for media files in development
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
