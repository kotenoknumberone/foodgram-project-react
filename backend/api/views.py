from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Follow

from .filters import IngredientFilter, RecipeFilter
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    SubscribesSerializer,
    TagSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):

    def get_queryset(self):
        if self.action == "following_list":
            return User.objects.filter(following__user=self.request.user)
        return self.queryset

    @action(
        detail=False,
        url_path="subscriptions",
        serializer_class=SubscribesSerializer,
    )
    def following_list(self, request):
        return self.list(request)


class SubscribeCreateDeleteView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, id):

        author = get_object_or_404(User, id=id)
        user = request.user

        if Follow.objects.filter(user=user, author=author).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user != author:
            Follow.objects.get_or_create(
                user=user,
                author=author,
            )
            follow = Follow.objects.get(user=user, author=author)
            serializer = FollowSerializer(follow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):

        author = get_object_or_404(User, id=id)
        user = request.user

        if Follow.objects.filter(user=user, author=author).exists():
            author = get_object_or_404(User, id=id)
            user = request.user

            subscribe = get_object_or_404(Follow, author=author, user=user)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


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

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, id):

        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        if Favorite.objects.filter(user=user, recipes=recipe).exists():
            return Response(
                "???? ?????? ???????????????? ???????????? ?? ??????????????????.",
            )
        Favorite.objects.get_or_create(
            recipes=recipe,
            user=user,
        )

        favorite = Favorite.objects.get(recipes=recipe, user=user)
        serializer = FavoriteSerializer(favorite)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        favorite = get_object_or_404(Favorite, recipes=recipe, user=user)
        favorite.delete()
        return Response(status=status.HTTP_200_OK)


class ShoppingCartCreateDeleteView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, id):

        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                "???? ?????? ???????????????? ???????????? ?? ???????????? ??????????????.",
            )
        ShoppingCart.objects.get_or_create(
            recipe=recipe,
            user=user,
        )

        shop_cart = ShoppingCart.objects.get(recipe=recipe, user=user)
        serializer = ShoppingCartSerializer(shop_cart)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user

        shop_cart = get_object_or_404(ShoppingCart, recipe=recipe, user=user)
        shop_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientApiViewSet(viewsets.ModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = [
        AllowAny,
    ]
    pagination_class = None


class RecipeModelViewSet(viewsets.ModelViewSet):

    filter_class = RecipeFilter
    permission_classes = [AdminOrAuthorOrReadOnly]
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["get"],
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
                amount = ingredient.amount
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                if name is not purchase_list:
                    purchase_list[name] = {
                        "measurement_unit": measurement_unit,
                        "amount": amount,
                    }
                else:
                    purchase_list[name]["amount"] += amount
        wishlist = []
        for item in purchase_list:
            wishlist.append(
                f'{item} - {purchase_list[item]["amount"]}'
                f'{purchase_list[item]["measurement_unit"]}\n'
            )
        wishlist.append("\n")
        wishlist.append("FoodGram, 2021")
        response = HttpResponse(wishlist, "Content-Type: application/pdf")
        response["Content-Disposition"] = 'attachment; filename="wishlist.pdf"'
        return response
