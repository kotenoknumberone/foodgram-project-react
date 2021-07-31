from users.models import Subscribe
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscribeCreateDeleteView, UserModelViewSet, SubscribeListView


router_1 = DefaultRouter()
router_1.register('users', UserModelViewSet, 'users')


urlpatterns = [
    path('', include(router_1.urls)),
    path('users/<int:id>/subscribe', 
         SubscribeCreateDeleteView.as_view(), 
         name='subscribe'),
    path('users/subscriptions', 
         SubscribeListView.as_view(), 
         name='subscribes_list'),
]     

