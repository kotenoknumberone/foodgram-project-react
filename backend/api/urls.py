from django.urls import include, path

from rest_framework.routers import DefaultRouter

from users.models import Subscribe
from .views import (IngredientApiViewSet, SubscribeCreateDeleteView,
                    SubscribeListView, TagApiViewSet, UserModelViewSet,
                    RecipeModelViewSet, FavoriteCreateDeleteView,
                    ShoppingCartCreateDeleteView,)

router = DefaultRouter()
router.register('users', UserModelViewSet, 'users')
router.register('tags', TagApiViewSet, 'tags')
router.register('ingredients', IngredientApiViewSet, 'ingredients')
router.register('recipes', RecipeModelViewSet, 'recipes')


urlpatterns = [
    path('', include(router.urls)),

    path('users/<int:id>/subscribe/', 
         SubscribeCreateDeleteView.as_view(), 
         name='subscribe'),     
    path('users/subscriptions/', 
         SubscribeListView.as_view(), 
         name='subscribes_list'),
    path('recipes/<int:id>/favorite/', 
         FavoriteCreateDeleteView.as_view(), 
         name='favorite'),
    path('recipes/<int:id>/shopping_cart/', 
         ShoppingCartCreateDeleteView.as_view(), 
         name='shopping_cart'),
]     

#не работает избранное, подписки
#
#
#