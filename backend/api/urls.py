from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (IngredientApiViewSet, 
                    TagApiViewSet, UserViewSet,
                    RecipeModelViewSet, FavoriteCreateDeleteView,
                    ShoppingCartCreateDeleteView, SubscribeCreateDeleteView)

router = DefaultRouter()
router.register('users', UserViewSet, 'users')
router.register('tags', TagApiViewSet, 'tags')
router.register('ingredients', IngredientApiViewSet, 'ingredients')
router.register('recipes', RecipeModelViewSet, 'recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:id>/subscribe/', 
         SubscribeCreateDeleteView.as_view(), 
         name='subscribe'),   
    path('recipes/<int:id>/favorite/', 
        FavoriteCreateDeleteView.as_view(), 
         name='favorite'),
    path('recipes/<int:id>/shopping_cart/', 
         ShoppingCartCreateDeleteView.as_view(), 
         name='shopping_cart'),
]     