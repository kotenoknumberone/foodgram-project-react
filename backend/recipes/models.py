from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):

    food_time = models.CharField(max_length=64, unique=True,)

    def __str__(self) -> str:
        return self.food_time


class Ingredient(models.Model):
    
    name = models.CharField(max_length=256)
    unit = models.CharField(max_length=64)

    def __str__(self) -> str:
        return '{},{}'.format(self.name, self.unit)


class Recipe(models.Model):

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,)
    title = models.CharField(max_length=256)
    image = models.ImageField(upload_to='recipes/',
                              blank=True,
                              null=True)
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe')
    tag = models.ManyToManyField(Tag)
    time = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.title


class IngredientRecipe(models.Model):

    ingredient = models.ForeignKey(Ingredient, 
                                   on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, 
                               on_delete=models.CASCADE)
    value = models.PositiveIntegerField()