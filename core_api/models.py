from django.db import models
from django.contrib.auth.models import User

#Ingredient Model
class Ingredient(models.Model):
    #
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(decimal_places=2, max_digits=10)
    unit_of_measure = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    pass

#Recipe Model
class Recipe(models.Model):
    #
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    batch_size = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    pass

class IngredientRecipe(models.Model):
    #
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    required_quantity = models.DecimalField(decimal_places=2, max_digits=10)
    unit_of_measure = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipe.name} - {self.required_quantity} {self.unit_of_measure} of {self.ingredient.name}"
    pass

