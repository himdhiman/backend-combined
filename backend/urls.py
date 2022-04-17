from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from backend import environment_variables

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("authentication.urls")),
    path("runcode/", include("runcode.urls")),
    path("problems/", include("problems.urls")),
]

if environment_variables.DEVELOPMENT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)