from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core_api.views import IngredientViewSet, RecipeViewSet, IngredientRecipeViewSet, InventoryView, download_csv, \
    RestockView, BrewView
from rest_framework_simplejwt.views import (
TokenObtainPairView,
TokenRefreshView,
)
from core_api.views import register_user

router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredient-recipes', IngredientRecipeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/inventory/<int:recipe_id>/', InventoryView.as_view(), name='inventory-check'),
    path('api/download/<str:model_name>/', download_csv, name='download-csv'),
    path('api/restock/<int:pk>/', RestockView.as_view(), name='restock'),
    path('api/brew/<int:recipe_id>/', BrewView.as_view(), name='brew'),
    path('api/register', register_user, name='register'),
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]