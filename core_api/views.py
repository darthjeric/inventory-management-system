from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Ingredient, Recipe, IngredientRecipe
from .serializers import IngredientSerializer, RecipeSerializer, IngredientRecipeSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class IngredientRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientRecipe.objects.all()
    serializer_class = IngredientRecipeSerializer

class InventoryView(APIView):
    def get(self, request, recipe_id, format=None):
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            return Response({"error": "Recipe not found"}, status=404)

        recipe_ingredients = IngredientRecipe.objects.filter(recipe=recipe)

        if not recipe_ingredients:
            return Response({"message": "This recipe has no ingredients defined."})

        max_brews = float('inf')

        for recipe_ingredient in recipe_ingredients:
            if recipe_ingredient.required_quantity == 0:
                continue

            brews_possible = recipe_ingredient.ingredient.quantity / recipe_ingredient.required_quantity

            if brews_possible < max_brews:
                max_brews = brews_possible

        return Response({
            "recipe_name": recipe.name,
            "batches_possible": int(max_brews),
            "batches_possible_exact": max_brews
        })