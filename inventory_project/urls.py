from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core_api.views import IngredientViewSet, RecipeViewSet, IngredientRecipeViewSet

router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredient-recipes', IngredientRecipeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]