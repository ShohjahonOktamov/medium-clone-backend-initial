from secrets import token_urlsafe
from typing import Type, Any

from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.db.models import Max, QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, permissions, generics, parsers, exceptions, viewsets, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from articles.models import Article
from articles.schemas import no_content_response, bad_request_response, unauthorized_response
from .authentications import CustomJWTAuthentication
from .errors import ACTIVE_USER_NOT_FOUND_ERROR_MSG
from .models import CustomUser, Recommendation, Follow, Notification
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ValidationErrorSerializer,
    TokenResponseSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    ForgotPasswordRequestSerializer,
    ForgotPasswordVerifyRequestSerializer,
    ResetPasswordResponseSerializer,
    ForgotPasswordVerifyResponseSerializer,
    ForgotPasswordResponseSerializer,
    RecommendationSerializer,
    NotificationSerializer
)
from .services import UserService, SendEmailService, OTPService

User: Type[CustomUser] = get_user_model()


@extend_schema_view(
    post=extend_schema(
        summary="Sign up a new user",
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: ValidationErrorSerializer
        }
    )
)
class SignupView(APIView):
    serializer_class = UserSerializer
    permission_classes = permissions.AllowAny,

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                'user': user_data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        summary="Log in a user",
        request=LoginSerializer,
        responses={
            200: TokenResponseSerializer,
            400: ValidationErrorSerializer,
        }
    )
)
class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Hisob maʼlumotlari yaroqsiz'}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema_view(
    get=extend_schema(
        summary="Get user information",
        responses={
            200: UserSerializer,
            400: ValidationErrorSerializer
        }
    ),
    patch=extend_schema(
        summary="Update user information",
        request=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer,
            400: ValidationErrorSerializer
        }
    )
)
class UsersMe(generics.RetrieveAPIView, generics.UpdateAPIView):
    http_method_names = ['get', 'patch']
    queryset = User.objects.filter(is_active=True)
    parser_classes = [parsers.MultiPartParser]
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer

    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


@extend_schema_view(
    post=extend_schema(
        summary="Log out a user",
        request=None,
        responses={
            200: ValidationErrorSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=None)
    def post(self, request, *args, **kwargs):
        UserService.create_tokens(request.user, access='fake_token', refresh='fake_token', is_force_add_to_redis=True)
        return Response({"detail": "Mufaqqiyatli chiqildi."})


@extend_schema_view(
    put=extend_schema(
        summary="Change user password",
        request=ChangePasswordSerializer,
        responses={
            200: TokenResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=request.user.username,
            password=serializer.validated_data['old_password']
        )

        if user is not None:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            tokens = UserService.create_tokens(user, is_force_add_to_redis=True)
            return Response(tokens)
        else:
            raise ValidationError("Eski parol xato.")


@extend_schema_view(
    post=extend_schema(
        summary="Forgot Password",
        request=ForgotPasswordRequestSerializer,
        responses={
            200: ForgotPasswordResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ForgotPasswordView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordRequestSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        users = User.objects.filter(email=email, is_active=True)
        if not users.exists():
            raise exceptions.NotFound(ACTIVE_USER_NOT_FOUND_ERROR_MSG)

        otp_code, otp_secret = OTPService.generate_otp(email=email, expire_in=2 * 60)

        try:
            SendEmailService.send_email(email, otp_code)
            return Response({
                "email": email,
                "otp_secret": otp_secret,
            })
        except Exception:
            redis_conn = OTPService.get_redis_conn()
            redis_conn.delete(f"{email}:otp")
            raise ValidationError("Emailga xabar yuborishda xatolik yuz berdi")


@extend_schema_view(
    post=extend_schema(
        summary="Forgot Password Verify",
        request=ForgotPasswordVerifyRequestSerializer,
        responses={
            200: ForgotPasswordVerifyResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ForgotPasswordVerifyView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordVerifyRequestSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        redis_conn = OTPService.get_redis_conn()
        otp_secret = kwargs.get('otp_secret')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data['otp_code']
        email = serializer.validated_data['email']
        users = User.objects.filter(email=email, is_active=True)
        if not users.exists():
            raise exceptions.NotFound(ACTIVE_USER_NOT_FOUND_ERROR_MSG)
        OTPService.check_otp(email, otp_code, otp_secret)
        redis_conn.delete(f"{email}:otp")
        token_hash = make_password(token_urlsafe())
        redis_conn.set(token_hash, email, ex=2 * 60 * 60)
        return Response({"token": token_hash})


@extend_schema_view(
    patch=extend_schema(
        summary="Reset Password",
        request=ResetPasswordResponseSerializer,
        responses={
            200: TokenResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ResetPasswordView(generics.UpdateAPIView):
    serializer_class = ResetPasswordResponseSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['patch']
    authentication_classes = []

    def patch(self, request, *args, **kwargs):
        redis_conn = OTPService.get_redis_conn()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_hash = serializer.validated_data['token']
        email = redis_conn.get(token_hash)

        if not email:
            raise ValidationError("Token yaroqsiz")

        users = User.objects.filter(email=email.decode(), is_active=True)
        if not users.exists():
            raise exceptions.NotFound(ACTIVE_USER_NOT_FOUND_ERROR_MSG)

        password = serializer.validated_data['password']
        user = users.first()
        user.set_password(password)
        user.save()

        update_session_auth_hash(request, user)
        tokens = UserService.create_tokens(user, is_force_add_to_redis=True)
        redis_conn.delete(token_hash)
        return Response(tokens)


@extend_schema_view(
    post=extend_schema(
        summary="Adjust Recommendations for an Article",
        request=RecommendationSerializer,
        responses={
            204: no_content_response,
            400: bad_request_response}
    )
)
class RecommendationView(APIView):
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        data: dict[str, int] = request.data

        more_article_id: int | None = data.get('more_article_id')
        less_article_id: None | int = data.get('less_article_id')

        if more_article_id and less_article_id:
            return Response(data={'error': 'Cannot provide both more_article_id and less_article_id.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not more_article_id and not less_article_id:
            return Response(data={'error': 'One of more_article_id or less_article_id must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if more_article_id:
            article: Article | None = get_object_or_404(klass=self.get_articles_queryset(), id=more_article_id)
            recommendation_type: str = 'more'
        elif less_article_id:
            article: None | Article = get_object_or_404(klass=self.get_articles_queryset(), id=less_article_id)
            recommendation_type: str = 'less'

        for topic in article.topics.all():
            recommendation: Recommendation | None = Recommendation.objects.filter(topic=topic).first()
            if recommendation:
                if recommendation.recommendation_type != recommendation_type:
                    recommendation.recommendation_type = recommendation_type
                    recommendation.save()
            else:
                Recommendation.objects.create(recommendation_type=recommendation_type, topic=topic)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_articles_queryset(self) -> QuerySet[Article]:
        return Article.objects.filter(status="publish")


@extend_schema_view(
    list=extend_schema(
        summary="Popular Authors List",
        request=None,
        responses={
            200: UserSerializer(many=True)
        }
    )
)
class PopularAuthorsView(ListAPIView):
    serializer_class: Type[UserSerializer] = UserSerializer

    def get_queryset(self) -> QuerySet[CustomUser]:
        articles = Article.objects.exclude(status__in=("trash", "archive"))

        authors_with_best_articles: QuerySet[dict[str, Any]] = articles.values('author__id').annotate(
            max_reads=Max('reads_count')
        )

        top_authors: QuerySet[dict[str, Any]] = authors_with_best_articles.order_by('-max_reads')[:5]

        top_author_ids: list[int] = [author['author__id'] for author in top_authors]

        queryset: QuerySet[CustomUser] = CustomUser.objects.filter(id__in=top_author_ids)

        return queryset


@extend_schema_view(
    post=extend_schema(
        summary="Follow Author",
        request=None,
        responses={
            201: "Mofaqqiyatli follow qilindi.",
            200: "Siz allaqachon ushbu foydalanuvchini kuzatyapsiz.",
            404: "No User matches the given query.",
            401: unauthorized_response
        }
    )
)
class AuthorFollowView(APIView):
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,
    permission_classes: tuple[Type[permissions.IsAuthenticated]] = permissions.IsAuthenticated,

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        user: CustomUser = request.user

        author: CustomUser = get_object_or_404(CustomUser, pk=pk)

        if Follow.objects.filter(followee=author, follower=user).exists():
            return Response(data={
                "detail": "Siz allaqachon ushbu foydalanuvchini kuzatyapsiz."
            }, status=status.HTTP_200_OK)

        Follow.objects.create(followee=author, follower=user)

        Notification.objects.create(user=author, message=f"{user.username} sizga follow qildi.")

        return Response(data={
            "detail": "Mofaqqiyatli follow qilindi."
        }, status=status.HTTP_201_CREATED)

    def delete(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        user: CustomUser = request.user

        author: CustomUser = get_object_or_404(CustomUser, pk=pk)

        follow: Follow = get_object_or_404(Follow, followee=author, follower=user)

        follow.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        summary="User Followers",
        request=None,
        responses={
            200: UserSerializer(many=True),
            401: unauthorized_response
        }
    )
)
class FollowersListView(ListAPIView):
    serializer_class: Type[UserSerializer] = UserSerializer
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,
    permission_classes: tuple[Type[permissions.IsAuthenticated]] = permissions.IsAuthenticated,

    def get_queryset(self) -> QuerySet[CustomUser]:
        author: CustomUser = self.request.user

        return CustomUser.objects.filter(followings__followee=author)


@extend_schema_view(
    list=extend_schema(
        summary="User Followings",
        request=None,
        responses={
            200: UserSerializer(many=True),
            401: unauthorized_response
        }
    )
)
class FollowingsListView(ListAPIView):
    serializer_class: Type[UserSerializer] = UserSerializer
    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,
    permission_classes: tuple[permissions.IsAuthenticated] = permissions.IsAuthenticated,

    def get_queryset(self) -> QuerySet[CustomUser]:
        user: CustomUser = self.request.user

        return CustomUser.objects.filter(followers__follower=user)


@extend_schema_view(
    list=extend_schema(
        summary="User Notifications",
        request=None,
        responses={
            200: NotificationSerializer(many=True),
            401: unauthorized_response
        }
    ),
    retrieve=extend_schema(
        summary="Notifications",
        request=None,
        responses={
            200: NotificationSerializer,
            404: "No Notification matches the given query.",
            401: unauthorized_response
        }
    )
)
class UserNotificationView(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    serializer_class: Type[NotificationSerializer] = NotificationSerializer

    authentication_classes: tuple[Type[CustomJWTAuthentication]] = CustomJWTAuthentication,
    permission_classes: tuple[Type[permissions.IsAuthenticated]] = permissions.IsAuthenticated,

    def get_queryset(self) -> QuerySet[Notification]:
        queryset: QuerySet[Notification] = Notification.objects.all()

        if self.request.method == "GET" and not self.kwargs.get("pk"):
            user: CustomUser = self.request.user
            queryset: QuerySet[Notification] = queryset.filter(user=user, read=False)

        return queryset

    @extend_schema(
        summary="Match Notification As Read",
        request=None,
        responses={
            204: no_content_response,
            404: "No Notification matches the given query."
        }
    )
    def partial_update(self, request: HttpRequest, pk: int, *args, **kwargs) -> Response:
        notification: Notification = get_object_or_404(klass=self.get_queryset(), pk=pk)

        super().partial_update(request=request, *args, **kwargs)

        if Notification.objects.get(pk=pk).read:
            notification.read = True
            notification.read_at = timezone.now()
            notification.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
