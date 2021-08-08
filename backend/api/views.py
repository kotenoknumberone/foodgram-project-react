from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse

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
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag, IngredientRecipe
from .serializers import (IngredientSerializer, SubscribeGetUserSerializer,
                          TagSerializer, UserRegistrationSerializer,
                          RecipeSerializer, RecipeCreateSerializer,
                          FavoriteSerializer, ShoppingCartSerializer,
                          FollowSerializer)


User = get_user_model()


class UserModelViewSet(UserViewSet):

    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()
    #lookup_field = 'username'
    #search_fields = ('username',)

    @action(
        detail=False,
        serializer_class=FollowSerializer,
    )
    def subscriptions(self, request):
        return self.list(request)

    @action(
        methods=['get', 'delete'],
        detail=True,
        serializer_class=FollowSerializer,
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response(
                {'errors': 'You cannot subscribe/unsubscribe to yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow = Subscribe.objects.filter(
            subscriber=user,
            author=author,
        ).first()

        if request.method == 'GET':
            if follow is not None:
                return Response(
                    {
                        'errors': (
                            'Follow object with given credentials '
                            'already exists'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Subscribe.objects.create(
                subscriber=user,
                author=author,
            )
            follow.save()
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if follow is None:
            return Response(
                {'errors': 'Follow object does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        if self.action == 'subscriptions':
            return User.objects.filter(
                following__user=self.request.user
            )
        return self.queryset

'''class SubscribeCreateDeleteView(APIView):

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
        return Response(status=status.HTTP_200_OK)'''


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


class DownloadPurchaseList(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = request.user
        shopping_cart = user.shoppingcart.all()
        purchase_list = {}
        for record in shopping_cart:
            recipe = record.recipe
            ingredients = IngredientRecipe.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amount = ingredient.amout
                name = ingredient.name
                measurement_unit = ingredient.measurement_unit
                if name is not purchase_list:
                    purchase_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    purchase_list[name]['amount'] = (
                        purchase_list[name]['amount'] + amount
                    )
        wishlist = []
        for item in purchase_list:
            wishlist.append(
                f'{item} - {purchase_list[item]["amount"]}'
                f'{purchase_list[item]["measurement_unit"]}/n'
            )
        wishlist.append('/n')
        wishlist.append('FoodGram, 2021')
        response = HttpResponse(wishlist, 'Content-Type: application/pdf')
        response['Content-Disposition'] = 'attachment; filename="wishlist.pdf"'
        return response
