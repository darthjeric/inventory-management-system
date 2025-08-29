from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core_api.views import IngredientViewSet, RecipeViewSet, IngredientRecipeViewSet, InventoryView

router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredient-recipes', IngredientRecipeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/inventory/<int:recipe_id>/', InventoryView.as_view(), name='inventory-check'),
    path('api/download/<str:model_name>/', download_csv, name='download-csv'),
]