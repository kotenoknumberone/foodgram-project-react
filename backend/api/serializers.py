from django.contrib.auth import get_user_model
from django.db.models import fields
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from djoser.serializers import \
    UserCreateSerializer as BaseUserRegistrationSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag, Favorite
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from users.models import Subscribe


User = get_user_model()


class UserRegistrationSerializer(BaseUserRegistrationSerializer):

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
        )


class DjoserUserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
        )


class SubscribeGetUserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    def get_is_subscribed(self, obj):
        user = Subscribe.objects.get(author=obj).subscriber
        return Subscribe.objects.filter(subscriber=user, author=obj).exists()

    class Meta:
        model = User
        fields = ('email', 
                  'id', 
                  'username',
                  'first_name', 
                  'last_name', 
                  'is_subscribed')


class SubscribeUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 
                  'id', 
                  'username',
                  'first_name', 
                  'last_name',)


class UserSerializer(DjoserUserSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 
                  'name', 
                  'color', 
                  'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit',)


class AddIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',)

    def get_ingredients(self, recipe):
        queryset = IngredientRecipe.objects.filter(recipe=recipe)
        return RecipeIngredientSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        user = self.context.get('request').user
        return Favorite.objects.filter(recipes=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(recipe=obj, user=user).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    class Meta:
        model = Recipe
        fields = ('ingredients',
                  'tags',
                  'image',
                  'name',
                  'text',
                  'cooking_time',)

    def to_representation(self, recipe):
        return RecipeSerializer(
            recipe,
            context={'request': self.context['request']}
        ).data

    def create(self, validated_data):

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient['id'],
            )
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient['amount']
            )
        return recipe

    def update(self, recipe, validated_data):

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount']
            )

        recipe.tags.remove()
        recipe.tags.set(tags)

        recipe.image = validated_data['image']
        recipe.name = validated_data['name']
        recipe.text = validated_data['text']
        recipe.cooking_time = validated_data['cooking_time']
        recipe.save()
        return recipe



class FavoriteSerializer(serializers.ModelSerializer):

    name = ReadOnlyField(source= 'recipes.name')
    cooking_time = ReadOnlyField(source='recipes.cooking_time')
    image =  Base64ImageField(read_only=True, source='recipes.image')

    class Meta:
        model = Favorite
        fields = ('id', 
                  'name',
                  'cooking_time',
                  'image',)


class ShoppingCartSerializer(serializers.ModelSerializer):

    name = ReadOnlyField(source='recipe.name')
    cooking_time = ReadOnlyField(source='recipe.cooking_time')
    image =  Base64ImageField(read_only=True, source='recipe.image')

    class Meta:
        model = ShoppingCart
        fields = ('id', 
                  'name',
                  'cooking_time',
                  'image',)



class SubscribeSerializer(serializers.ModelSerializer):

    author = SubscribeUserSerializer(required=True)
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = Subscribe
        fields = ("author", "recipes")
        validators = [UniqueTogetherValidator(
            queryset=Subscribe.objects.all(),
            fields=['subscriber', 'author'])]


class ShowFollowerRecipeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        max_length=None,
        required=True,
        allow_empty_file=False,
        use_url=True,
    )

    class Meta:
        model = Recipe
        fields = ('id', 
                  'name', 
                  'image', 
                  'cooking_time')


class ShowFollowersSerializer(serializers.ModelSerializer):

    recipes = ShowFollowerRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('email', 
                  'id', 
                  'username', 
                  'first_name',
                  'last_name', 
                  'recipes',)


class FollowSerializer(UserSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
