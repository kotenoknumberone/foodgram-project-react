from django.urls import include, path

from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import (IngredientApiViewSet, SubscribeListViewSet, SubscribeCreateDeleteView, 
                    TagApiViewSet, UserModelViewSet,
                    RecipeModelViewSet, FavoriteCreateDeleteView,
                    ShoppingCartCreateDeleteView,
                    DownloadPurchaseList, showfollows)

router = DefaultRouter()
#router_2 = SimpleRouter(trailing_slash=True)
router.register('users', UserModelViewSet, 'users')
router.register('tags', TagApiViewSet, 'tags')
router.register('ingredients', IngredientApiViewSet, 'ingredients')
router.register('recipes', RecipeModelViewSet, 'recipes')
#router_2.register('users/subscriptions', SubscribeListViewSet, 'subscriptions')


urlpatterns = [
    path('', include(router.urls)),
    #path('', include(router_2.urls)),

    path('users/<int:id>/subscribe/', 
         SubscribeCreateDeleteView.as_view(), 
         name='subscribe'),
     #path('users/subscriptions/',
        # showfollows, name='users_subs'),     
    #path('users/subscriptions', 
     #    SubscribeListView.as_view(), 
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