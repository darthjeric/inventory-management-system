from django.contrib import admin
from .models import Ingredient, Recipe, IngredientRecipe
from django.http import HttpResponse
import csv


def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model.__name__}.csv"'

    writer = csv.writer(response)

    field_names = [field.name for field in querset.model._meta.fields]
    writer.writerow(field_names)

    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response

export_as_csv.short_description = "Export Selected as CSV"

# Register your models here.
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_added']
    readonly_fields = ['date_added']
    actions = [export_as_csv]

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_added']
    readonly_fields = ['date_added']
    actions = [export_as_csv]

@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ['ingredient', 'date_added']
    readonly_fields = ['date_added']
    actions = [export_as_csv]
