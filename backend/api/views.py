from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated, 
                                        IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import AdminOrAuthorOrReadOnly
from .filters import RecipeFilter
from users.models import Follow
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag, IngredientRecipe
from .serializers import (IngredientSerializer, 
                          TagSerializer,
                          RecipeSerializer, RecipeCreateSerializer,
                          FavoriteSerializer, ShoppingCartSerializer,
                          FollowSerializer, UserSerializer)


User = get_user_model()


class UserViewSet(DjoserUserViewSet):

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=['get', 'delete'],
        detail=True,
        serializer_class=FollowSerializer,
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'GET':
            data = {'user': user.id, 'author': id}
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            output = UserSerializer(author, context={'request': request})
            return Response(output.data, status=status.HTTP_201_CREATED)

        try:
            follow = Follow.objects.get(user=user, author=author)
        except ObjectDoesNotExist:
            raise ValidationError({'errors': 'Follow object does not exist'})

        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        serializer_class=UserSerializer,
    )
    def subscriptions(self, request):
        return self.list(request)

    def get_queryset(self):
        if self.action == 'subscriptions':
            return User.objects.filter(
                following__user=self.request.user
            )
        return self.queryset


class TagApiViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Tag.objects.all()
        tag = get_object_or_404(queryset, pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)     


class FavoriteCreateDeleteView(APIView):

    permission_classes = [IsAuthenticated, ]

    def get(self, request, id):

        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        if Favorite.objects.filter(user=user, 
                                   recipes=recipe).exists():
            return Response('Вы уже добавили рецепт в избранное.',)
        Favorite.objects.get_or_create(recipes=recipe, 
                                       user=user,)

        favorite = Favorite.objects.get(recipes=recipe, user=user)                            
        serializer = FavoriteSerializer(favorite)

        return Response(serializer.data, 
                        status=status.HTTP_200_OK)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        favorite = get_object_or_404(Favorite, 
                                      recipes=recipe,
                                      user=user)
        favorite.delete()
        return Response(status=status.HTTP_200_OK)


class ShoppingCartCreateDeleteView(APIView):

    permission_classes = [IsAuthenticated, ]

    def get(self, request, id):

        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        if ShoppingCart.objects.filter(user=user, 
                                       recipe=recipe).exists():
            return Response('Вы уже добавили рецепт в список покупок.',)
        ShoppingCart.objects.get_or_create(recipe=recipe, 
                                           user=user,)

        shop_cart = ShoppingCart.objects.get(recipe=recipe, 
                                             user=user)                            
        serializer = ShoppingCartSerializer(shop_cart)

        return Response(serializer.data, 
                        status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        shop_cart = get_object_or_404(ShoppingCart, 
                                      recipe=recipe,
                                      user=user)
        shop_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientApiViewSet(viewsets.ViewSet):
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    permission_classes = [AllowAny, ]
    
    def list(self, request):
        queryset = Ingredient.objects.all()
        serializer = IngredientSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Ingredient.objects.all()
        ingredient = get_object_or_404(queryset, pk=pk)
        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data)   


class RecipeModelViewSet(viewsets.ModelViewSet):

    #filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = [AdminOrAuthorOrReadOnly]
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer    
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        purchase_list = {}

        for record in shopping_cart:
            recipe = record.recipe
            ingredients = IngredientRecipe.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                ingredient = ingredient.ingredient
                
            purchase_list[ingredient] = (
                purchase_list[ingredient]
                    )
        wishlist = []
        for item in purchase_list:
            wishlist.append(
                f'{item} - {purchase_list[item]["ingredient"]}'
                f'{purchase_list[item]["ingredient"]}/n'
            )
        wishlist.append('/n')
        wishlist.append('FoodGram, 2021')
        response = HttpResponse(wishlist, 'Content-Type: application/pdf')
        response['Content-Disposition'] = 'attachment; filename="wishlist.pdf"'
        return response
