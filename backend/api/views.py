from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from djoser.views import UserViewSet

from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated, 
                                        IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import AdminOrAuthorOrReadOnly
from .filters import RecipeFilter
from users.models import Subscribe
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (IngredientSerializer, SubscribeGetUserSerializer,
                          SubscribeSerializer, SubscribeUserSerializer,
                          TagSerializer, UserRegistrationSerializer,
                          RecipeSerializer, RecipeCreateSerializer,
                          FavoriteSerializer, ShoppingCartSerializer)


User = get_user_model()


class UserModelViewSet(UserViewSet):

    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    search_fields = ('username',)


class SubscribeCreateDeleteView(APIView):

    permission_classes = [IsAuthenticated, ]

    def get(self, request, id):

        author = get_object_or_404(User, id=id)
        subscriber = request.user

        if Subscribe.objects.filter(subscriber=subscriber, 
                                    author=author).exists():
            return Response('Вы уже подписаны',)
        if subscriber != author:
            Subscribe.objects.get_or_create(subscriber=subscriber, 
                                            author=author,)
            serializer = SubscribeGetUserSerializer(author)
            return Response(serializer.data, 
                            status=status.HTTP_200_OK)

    def delete(self, request, id):

        author = get_object_or_404(User, id=id)
        subscriber = request.user

        subscribe = get_object_or_404(Subscribe, 
                                      author=author,
                                      subscriber=subscriber)
        subscribe.delete()
        return Response(status=status.HTTP_200_OK)


class SubscribeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = SubscribeSerializer
    allowed_methods = ['GET', ]

    def get_queryset(self):
        return Subscribe.objects.filter(subscriber=self.request.user)
    

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
