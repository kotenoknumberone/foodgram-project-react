from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from djoser.serializers import \
    UserCreateSerializer as BaseUserRegistrationSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from rest_framework import serializers
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


class SubscribeSerializer(serializers.ModelSerializer):

    author = SubscribeUserSerializer(required=True)

    class Meta:
        model = Subscribe
        fields = ("author",)
        validators = [UniqueTogetherValidator(
            queryset=Subscribe.objects.all(),
            fields=['subscriber', 'author'])]


class UserSerializer(DjoserUserSerializer):
    #is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
        )

    '''def get_is_subscribed(self, subscriber):
        author = self.context['request'].subscriber
        if not author.is_authenticated:
            return False
        return Subscribe.objects.filter(subscriber=subscriber, author=author).exists()'''


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


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
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, recipe):
        queryset = IngredientRecipe.objects.filter(recipe=recipe)
        return RecipeIngredientSerializer(queryset, many=True).data


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

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


