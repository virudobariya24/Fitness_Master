from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Task (2): Django Admin (allows manually adding admin users)
    path('admin/', admin.site.urls),

    # Task (1): Admin Authentication (Login & Logout)
    path('', include('accounts.urls')),

    # Task (4), (5), (6): Bootstrap Admin Dashboard & Packages Management
    path('', include('packages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
