from django.urls import include, path

from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import (IngredientApiViewSet, SubscribeCreateDeleteView, 
                    TagApiViewSet, UserModelViewSet,
                    RecipeModelViewSet, FavoriteCreateDeleteView,
                    ShoppingCartCreateDeleteView,
                    DownloadPurchaseList,)

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
    #path('users/subscriptions', 
    #   SubscribeListViewSet.as_view(), 
    #    name='subscribes_list'),
    path('recipes/<int:id>/favorite/', 
         FavoriteCreateDeleteView.as_view(), 
         name='favorite'),
    path('recipes/<int:id>/shopping_cart/', 
         ShoppingCartCreateDeleteView.as_view(), 
         name='shopping_cart'),
     path('recipes/download_shopping_cart',
         DownloadPurchaseList.as_view(), name='dowload_shopping_cart'),
]     

#не работает избранное, подписки
#
#
#