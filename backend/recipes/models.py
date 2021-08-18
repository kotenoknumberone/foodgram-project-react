from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):

    name = models.CharField(max_length=200)
    color = ColorField(null=True, format="hex")
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):

    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=64)

    def __str__(self) -> str:
        return "{},{}".format(self.name, self.measurement_unit)


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        verbose_name="Автор",
    )
    name = models.CharField(max_length=256, verbose_name="Название")
    image = models.ImageField(
        upload_to="recipes/images/",
        blank=True,
        null=True,
        verbose_name="Изображение",
    )
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        blank=True,
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(Tag, verbose_name="Тэги")
    cooking_time = models.PositiveIntegerField(verbose_name="Время")

    def __str__(self) -> str:
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Ингредиент",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество",
    )


class Favorite(models.Model):
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепты",
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )

    class Meta:
        verbose_name = "Избранное"


class ShoppingCart(models.Model):

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )

    class Meta:
        verbose_name = "Список покупок"
