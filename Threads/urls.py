from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/dashboard/', admin.site.urls),
    path('posts/', include('posts.urls')),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('accounts.urls')),
    # path('', include('core.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)