from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserModelViewSet


router = DefaultRouter()
router.register('users', UserModelViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
]
