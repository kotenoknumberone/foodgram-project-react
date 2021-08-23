from django.contrib.auth import get_user_model
from django.core import exceptions
from django.core.exceptions import ValidationError
from django.db.models import fields
from django.shortcuts import get_object_or_404
from djoser.serializers import (
    UserCreateSerializer as DjoserRegistrationSerializer,
)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Follow

User = get_user_model()


class UserRegistrationSerializer(DjoserRegistrationSerializer):
    class Meta(DjoserRegistrationSerializer.Meta):
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        )


class UserSerializer(DjoserUserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        )

    def get_is_subscribed(self, user):
        author = self.context["request"].user
        if author.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=author).exists()


class ShowAuthorRecipeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        max_length=None,
        required=True,
        allow_empty_file=False,
        use_url=True,
    )

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribesSerializer(DjoserUserSerializer):

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField("get_author_recipes")
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_author_recipes(self, obj):
        recipes_limit = self.context.get("request").GET.get(
            "recipes_limit", None
        )
        if not recipes_limit is None:
            recipes = Recipe.objects.filter(author=obj)[: int(recipes_limit)]
            serializer = ShowAuthorRecipeSerializer(
                data=recipes,
                many=True,
            )
            serializer.is_valid()
            return serializer.data
        recipes = Recipe.objects.filter(author=obj)
        serializer = ShowAuthorRecipeSerializer(
            data=recipes,
            many=True,
        )
        serializer.is_valid()
        return serializer.data

    def get_is_subscribed(self, user):
        author = self.context["request"].user
        if author.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=author).exists()

    def get_recipes_count(self, user):
        recipes = Recipe.objects.all().filter(author=user)
        return len(recipes)


class FollowSerializer(UserSerializer):
    class Meta:
        model = Follow
        fields = ("user", "author")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class AddIngredientSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class IngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeSerializer(serializers.ModelSerializer):

    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(recipes=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingCart.objects.filter(recipe=obj, user=user).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def create(self, validated_data):

        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.save()
        recipe.tags.set(tags)

        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient["id"]),
                amount=ingredient["amount"],
            )
        return recipe

    def update(self, instance, validated_data):

        ingredients = validated_data.pop("ingredients")
        IngredientRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop("tags")

        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=get_object_or_404(Ingredient, id=ingredient["id"]),
                recipe=instance,
                amount=ingredient["amount"],
            )

        instance.name = validated_data.pop("name")
        instance.text = validated_data.pop("text")
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.pop("cooking_time")
        instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = RecipeSerializer(
            instance, context={"request": self.context["request"]}
        ).data
        return data


class FavoriteSerializer(serializers.ModelSerializer):

    name = ReadOnlyField(source="recipes.name")
    cooking_time = ReadOnlyField(source="recipes.cooking_time")
    image = Base64ImageField(read_only=True, source="recipes.image")

    class Meta:
        model = Favorite
        fields = (
            "id",
            "name",
            "cooking_time",
            "image",
        )


class ShoppingCartSerializer(serializers.ModelSerializer):

    name = ReadOnlyField(source="recipe.name")
    cooking_time = ReadOnlyField(source="recipe.cooking_time")
    image = Base64ImageField(read_only=True, source="recipe.image")

    class Meta:
        model = ShoppingCart
        fields = (
            "id",
            "name",
            "cooking_time",
            "image",
        )
