import re
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets, status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from djoser.views import UserViewSet
from .serializers import SubscribeSerializer, UserRegistrationSerializer
from .serializers import SubscribeUserSerializer, SubscribeGetUserSerializer
from .serializers import TagSerializer
from users.models import Subscribe
from recipes.models import Tag, IngredientRecipe, Ingredient, Recipe


User = get_user_model()


class UserModelViewSet(UserViewSet):

    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    search_fields = ('username',)


class SubscribeCreateDeleteView(APIView):

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
