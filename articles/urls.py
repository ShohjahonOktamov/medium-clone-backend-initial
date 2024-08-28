from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ArticlesView, TopicFollowView, CreateCommentsView, ArticleDetailCommentsView, CommentsView

router = DefaultRouter()
router.register(prefix='', viewset=ArticlesView, basename='articles')
router.register(prefix=r'comments', viewset=CommentsView, basename='comments')

urlpatterns: list = [
    path('', include(router.urls)),
    path('topics/<int:pk>/follow/', TopicFollowView.as_view(), name='topic-follow'),
    path('<int:pk>/comments/', CreateCommentsView.as_view(), name='create-comment'),
    path('<int:pk>/detail/comments/', ArticleDetailCommentsView.as_view(), name='detail-article-comments')
]
