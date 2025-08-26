from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, LogoutSerializer, ProfileSerializer, FollowSerializer
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, parser_classes
from django.shortcuts import get_object_or_404
from .models import User, UserFollow

class RegisterView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user, context={'request': request}).data
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Foydalanuvchi muvaffaqiyatli yaratildi",
                "user": user_data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView): 
    # permission_classes = [AllowAny]  

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user, context={'request': request}).data
            return Response({
                "message": "Tizimga muvaffaqiyatli kirildi!",
                "user": user_data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Tizimdan muvaffaqiyatli chiqildi!", }, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    lookup_field = 'username'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # serializerda .get_is_owner ishlashi uchun
        return context

    def get_object(self):
        return get_object_or_404(self.get_queryset(), username=self.kwargs['username'])

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_authenticated or request.user != obj:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Siz faqat o'z profilingizni o'zgartira olasiz.")
        return super().update(request, *args, **kwargs)
    

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def check_username(request):
    username = request.data.get('username')
    if not username:
        return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"available": False, "message": "Username already taken."})
    return Response({"available": True})


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def check_email(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"available": False, "message": "Email already taken."})
    return Response({"available": True})


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def check_phone(request):
    phone = request.data.get('phone')
    if not phone:
        return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(phone=phone).exists():
        return Response({"available": False, "message": "Phone number already taken."})
    return Response({"available": True})


class AuthCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'user': request.user.username}, status=status.HTTP_200_OK)
    

class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        follower = request.user
        following = get_object_or_404(User, username=username)

        if follower == following:
            return Response(
                {"detail": "O'zingizni follow qilib bo'lmaydi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow_instance = UserFollow.objects.filter(
            follower=follower,
            following=following
        ).first()

        if follow_instance:
            follow_instance.delete()
            return Response({"detail": "Unfollowed"}, status=status.HTTP_204_NO_CONTENT)
        else:
            UserFollow.objects.create(follower=follower, following=following)
            return Response({"detail": "Followed"}, status=status.HTTP_201_CREATED)
    

class FollowersView(APIView):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)

        followers_qs = UserFollow.objects.filter(following=user).select_related('follower')
        followers = [follow.follower for follow in followers_qs]  # faqat userlar

        data = UserSerializer(followers, many=True, context={'request': request})
        return Response({"followers": data.data}, status=status.HTTP_200_OK)


class FollowingView(APIView):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)

        following_qs = UserFollow.objects.filter(follower=user).select_related('following')
        followings = [follow.following for follow in following_qs]  # faqat userlar

        data = UserSerializer(followings, many=True, context={'request': request})
        return Response({"following": data.data}, status=status.HTTP_200_OK)
