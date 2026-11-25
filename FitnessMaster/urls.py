from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Task (2): Django Admin (accessible at /django-admin/ for manually adding admin users)
    path('django-admin/', admin.site.urls),

    # Task (1): Admin & User Authentication, Root User Panel, and Admin Gateway (/admin/)
    path('', include('accounts.urls')),

    # Task (4), (5), (6): Bootstrap Admin Dashboard & Packages Management
    path('', include('packages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
