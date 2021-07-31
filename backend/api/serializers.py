from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
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
            fields=['user', 'author'])]