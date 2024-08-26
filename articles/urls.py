from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ArticlesView

router: DefaultRouter = DefaultRouter()

router.register(prefix='', viewset=ArticlesView)

urlpatterns = router.urls
