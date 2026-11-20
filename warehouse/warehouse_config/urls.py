from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("warehouse-admin/", admin.site.urls),
    path("api/warehouse/", include("inventory.urls")),
    path("api/warehouse/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/warehouse/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/warehouse/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/warehouse/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
