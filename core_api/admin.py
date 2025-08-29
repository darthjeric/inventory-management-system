from django.contrib import admin
from .models import Ingredient, Recipe, IngredientRecipe

# Register your models here.
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_added']
    readonly_fields = ['date_added']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_added']
    readonly_fields = ['date_added']

@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ['ingredient', 'date_added']
    readonly_fields = ['date_added']