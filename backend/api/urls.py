from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (IngredientApiViewSet, 
                    TagApiViewSet, UserViewSet,
                    RecipeModelViewSet, FavoriteCreateDeleteView,
                    ShoppingCartCreateDeleteView,)

router = DefaultRouter()
router.register('users', UserViewSet, 'users')
router.register('tags', TagApiViewSet, 'tags')
router.register('ingredients', IngredientApiViewSet, 'ingredients')
router.register('recipes', RecipeModelViewSet, 'recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:id>/favorite/', 
        FavoriteCreateDeleteView.as_view(), 
         name='favorite'),
    path('recipes/<int:id>/shopping_cart/', 
         ShoppingCartCreateDeleteView.as_view(), 
         name='shopping_cart'),
]     
