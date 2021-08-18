import django_filters as filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = filters.BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("is_favorited", "is_in_shopping_cart", "author", "tags")

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorite__user=user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shoppingcart__user=user)
        return Recipe.objects.all()


class IngredientFilter(filters.FilterSet):

    name = filters.CharFilter(field_name="name", lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ("name",)
