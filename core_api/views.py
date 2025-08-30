from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Ingredient, Recipe, IngredientRecipe
from .serializers import IngredientSerializer, RecipeSerializer, IngredientRecipeSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from decimal import Decimal, InvalidOperation

import csv
from django.http import HttpResponse

from django.db import transaction

from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IngredientRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientRecipe.objects.all()
    serializer_class = IngredientRecipeSerializer

    def get_queryset(self):
        queryset = self.queryset

        recipe_id = self.request.query_params.get('recipe')

        if recipe_id:
            queryset = queryset.filter(recipe_id=recipe_id)
            
        return queryset


class InventoryView(APIView):
    def get(self, request, recipe_id, format=None):
        try:
            recipe = Recipe.objects.get(pk=recipe_id, user=request.user)
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
        ingredient = get_object_or_404(Ingredient, pk=pk, user=request.user)

        try:
            restock_quantity = Decimal(request.data.get('quantity'))
        except (InvalidOperation, TypeError):
            return Response({"error": "A 'quantity' field with a valid number is required."}, status=400)

        ingredient.quantity += restock_quantity
        ingredient.save()

        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data)

class BrewView(APIView):
    def patch(self, request, recipe_id, format=None):
        try:
            recipe = Recipe.objects.get(pk=recipe_id, user=request.user)
        except Recipe.DoesNotExist:
            return Response({"error": "Recipe not found"}, status=404)

        # Get all required ingredients for the recipe in a single query
        recipe_ingredients = IngredientRecipe.objects.filter(recipe=recipe)

        if not recipe_ingredients:
            return Response({"message": "This recipe has no ingredients defined."})

        # Check for sufficient ingredients first (Crucial step!)
        with transaction.atomic():
            for recipe_ingredient in recipe_ingredients:
                ingredient_on_hand = recipe_ingredient.ingredient
                required_quantity = recipe_ingredient.required_quantity

                # We need to add a way to handle unit conversions here
                # For now, we assume units match.
                if ingredient_on_hand.quantity < required_quantity:
                    return Response({
                        "error": f"Insufficient {ingredient_on_hand.name}. Need {required_quantity} {recipe_ingredient.unit_of_measure}, but only have {ingredient_on_hand.quantity} {ingredient_on_hand.unit_of_measure}."
                    }, status=400)

            # If all checks pass, subtract the quantities
            for recipe_ingredient in recipe_ingredients:
                ingredient_on_hand = recipe_ingredient.ingredient
                required_quantity = recipe_ingredient.required_quantity

                ingredient_on_hand.quantity -= required_quantity
                ingredient_on_hand.save()  # Save the updated quantity to the database

        return Response({
            "message": f"Successfully brewed one batch of '{recipe.name}'. Inventory has been updated."
        })

@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer