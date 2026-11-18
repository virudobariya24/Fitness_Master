from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Built-in fallback admin
    path('django-admin/', admin.site.urls),
    
    # 1. Public Website
    path('', include('core.urls')),
    
    # 2. Authentication & Accounts
    path('auth/', include('accounts.urls')),
    
    # 3. User Panel (Dashboard, Workouts, Nutrition, Tracking, Challenges)
    path('user/', include('dashboard.urls')),
    path('user/workouts/', include('workouts.urls')),
    path('user/nutrition/', include('nutrition.urls')),
    path('user/tracking/', include('tracking.urls')),
    path('user/challenges/', include('challenges.urls')),
    
    # 4. Custom Admin Panel (accessible via /custom-admin/ and /admin/)
    path('custom-admin/', include('custom_admin.urls')),
    path('admin/', RedirectView.as_view(url='/custom-admin/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
