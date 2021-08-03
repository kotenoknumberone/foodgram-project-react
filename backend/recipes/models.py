from django.db import models
from django.contrib.auth import get_user_model
from colorfield.fields import ColorField


User = get_user_model()


class Tag(models.Model):

    name = models.CharField(max_length=200)
    color = ColorField(null=True, format='hex')
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=64)

    def __str__(self) -> str:
        return '{},{}'.format(self.name, self.measurement_unit)


class Recipe(models.Model):

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=False, null=True,)
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='recipes/images',
                              blank=True,
                              null=True)
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',)
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, 
                                   on_delete=models.CASCADE,
                                   null=True)
    recipe = models.ForeignKey(Recipe, 
                               on_delete=models.CASCADE,)
    amount = models.PositiveIntegerField()


class Favorite(models.Model):
    recipes = models.ForeignKey(Recipe,
                                on_delete=models.CASCADE,
                                verbose_name='Рецепты'
    )
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Избранное'