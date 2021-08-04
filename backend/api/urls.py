from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.models import Subscribe

from .views import (IngredientApiViewSet, SubscribeCreateDeleteView,
                    SubscribeListView, TagApiViewSet, UserModelViewSet,
                    RecipeModelViewSet, FavoriteCreateDeleteView,
                    ShoppingCartCreateDeleteView,)

router_1 = DefaultRouter()
router_1.register('users', UserModelViewSet, 'users')
router_2 = DefaultRouter()
router_2.register('tags', TagApiViewSet, 'tags')
router_3 = DefaultRouter()
router_3.register('ingredients', IngredientApiViewSet, 'ingredients')
router_4 = DefaultRouter()
router_4.register('recipes', RecipeModelViewSet, 'recipes')



urlpatterns = [
    path('', include(router_1.urls)),
    path('', include(router_2.urls)),
    path('', include(router_3.urls)),
    path('', include(router_4.urls)),
    path('users/<int:id>/subscribe', 
         SubscribeCreateDeleteView.as_view(), 
         name='subscribe'),     
    path('users/subscriptions', 
         SubscribeListView.as_view(), 
         name='subscribes_list'),
    path('recipes/<int:id>/favorite/', 
         FavoriteCreateDeleteView.as_view(), 
         name='favorite'),
    path('recipes/<int:id>/shopping_cart/', 
         ShoppingCartCreateDeleteView.as_view(), 
         name='shopping_cart'),
]     

