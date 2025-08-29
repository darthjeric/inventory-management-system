from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Ingredient, Recipe, IngredientRecipe
from .serializers import IngredientSerializer, RecipeSerializer, IngredientRecipeSerializer
from django.shortcuts import get_object_or_404
from decimal import Decimal

import csv
from django.http import HttpResponse

def download_csv(request, model_name):
    model_name = model_name.lower()

    if model_name == 'ingredients':
        model = Ingredient
        queryset = Ingredient.objects.all()
    elif model_name == 'recipes':
        model = Recipe
        queryset = Recipe.objects.all()
    elif model_name == 'ingredient-recipes':
        model = IngredientRecipe
        queryset = IngredientRecipe.objects.all()
    else:
        return HttpResponse('Invalid model name', status=400)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{model_name}.csv"'

    writer = csv.writer(response)

    field_names = [field.name for field in model._meta.fields]
    writer.writerow(field_names)

    for obj in queryset:
        row_data = [getattr(obj, field) for field in field_names]
        writer.writerow(row_data)

    return response

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

class RestockView(APIView):
    def patch(self, request, pk, format=None):
        ingredient = get_object_or_404(Ingredient, pk=pk)

        restock_quantity = request.data.get('quantity')

        if restock_quantity is None or not isinstance(restock_quantity, (int, float, str)):
            return Response({"error": "A 'quantity' field with a valid number is required."}, status=400)

        restock_quantity = Decimal(restock_quantity)

        ingredient.quantity += restock_quantity
        ingredient.save()

        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data)