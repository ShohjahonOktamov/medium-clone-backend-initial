from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router: DefaultRouter = DefaultRouter()
router.register(prefix=r"notifications", viewset=views.UserNotificationView, basename="notifications")

urlpatterns: list = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('me/', views.UsersMe.as_view(), name='users-me'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password/change/', views.ChangePasswordView.as_view(), name='change-password'),
    path('password/forgot/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('password/forgot/verify/<str:otp_secret>/', views.ForgotPasswordVerifyView.as_view(),
         name="forgot-verify"),
    path('password/reset/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('recommend/', views.RecommendationView.as_view(), name='recommendation'),
    path('articles/popular/', views.PopularAuthorsView.as_view(), name='users-top-authors'),
    path('<int:pk>/follow/', views.AuthorFollowView.as_view(), name='users-follow-unfollow-authors'),
    path('followers/', views.FollowersListView.as_view(), name='users-followers'),
    path('following/', views.FollowingsListView.as_view(), name='users-followings'),
    path('', include(router.urls))
    # path('notifications/', views.UserNotificationView.as_view(), name='notification-list'),
    # path('notifications/<int:pk>/', views.UserNotificationView.as_view(), name='notification-detail'),
]
