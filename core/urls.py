from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from django.contrib.auth.decorators import user_passes_test

def is_authenticated(user):
    return user.is_authenticated

urlpatterns = [
    path("admin/", admin.site.urls),
    path('health/', lambda _: JsonResponse({'detail': 'Healthy'}), name='health'),
    path('users/', include('users.urls')),
    path('schema/', user_passes_test(is_authenticated)(SpectacularAPIView.as_view()), name='schema'),
    path('swagger/', user_passes_test(is_authenticated)(SpectacularSwaggerView.as_view()), name='swagger-ui'),
    path('redoc/', user_passes_test(is_authenticated)(SpectacularRedocView.as_view()), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
