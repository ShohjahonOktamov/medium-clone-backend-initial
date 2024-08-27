from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ArticlesView, TopicFollowView

router = DefaultRouter()
router.register(prefix='', viewset=ArticlesView, basename='articles')

urlpatterns: list = [
    path('', include(router.urls)),
    path('topics/<int:pk>/follow/', TopicFollowView.as_view(), name='topic-follow'),
]
