from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from .models import Ingredient, IngredientRecipe, Recipe, Tag


class IngredientRecipeInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInLine,)


admin.site.register(Ingredient)
admin.site.register(IngredientRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)