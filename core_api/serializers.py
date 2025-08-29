from rest_framework import serializers
from .models import Ingredient, Recipe, IngredientRecipe

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = IngredientRecipe
        fields = ['ingredient_name', 'required_quantity', 'unit_of_measure']

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(source='ingredientrecipe_set', many=True, read_only=True)
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'description', 'batch_size', 'ingredients', 'date_added']

class IngredientRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientRecipe
        fields = '__all__'

