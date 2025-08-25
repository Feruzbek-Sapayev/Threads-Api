from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.translation import gettext_lazy as _
from accounts.models import User, UserFollow
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'fullname', 'bio', 'photo', 'link') 
    
    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and hasattr(obj.photo, 'url'):
            return request.build_absolute_uri(obj.photo.url)
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'fullname', 'password')

    def create(self, validated_data):
        user = User(**validated_data)
        password = validated_data.pop('password')
        try:
            validate_password(password, user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("login")
        password = attrs.get("password")

        user = None

        # Har xil maydonlar orqali aniqlashga harakat qilamiz
        if "@" in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError(_("Email noto‘g‘ri"))
        elif identifier.startswith("+") or identifier.isdigit():
            try:
                user_obj = User.objects.get(phone=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError(_("Telefon raqam noto‘g‘ri"))
        else:
            try:
                user_obj = User.objects.get(username=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError(_("Username noto‘g‘ri"))

        # Parolni tekshirish
        if not user_obj.check_password(password):
            raise serializers.ValidationError(_("Parol noto‘g‘ri"))

        if not user_obj.is_active:
            raise serializers.ValidationError(_("Foydalanuvchi aktiv emas"))

        attrs["user"] = user_obj
        return attrs
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError(_("Token allaqachon yaroqsiz yoki noto‘g‘ri"))
        

class ProfileSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'fullname', 'bio', 'photo', 'link', 'is_owner', 'posts', 'followers_count', 'following_count')
        read_only_fields = ('is_owner', 'posts')

    def get_is_owner(self, obj):
        request = self.context.get('request')
        print(request.user, obj)
        return request.user == obj

    def get_posts(self, obj):
        from ..posts import PostSerializer  
        request = self.context.get('request') 
        return PostSerializer(obj.posts.all().order_by('-created_at'), many=True, context={'request': request}).data

    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        
        # Check if is_owner is False
        if not representation.get('is_owner'):
            # Remove email and phone fields
            representation.pop('email', None)
            representation.pop('phone', None)
            
        return representation
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
        


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.SerializerMethodField()

    class Meta:
        model = UserFollow
        fields = ['id', 'follower']
        read_only_fields = ['id', 'created_at', 'follower']

    def validate(self, data):
        user = self.context['request'].user
        following = data['following']

        if user == following:
            raise serializers.ValidationError("O'zingizni follow qilib bo'lmaydi.")
        return data
    
    def get_follower(self, obj):
        user = obj.follower
        return {
            "id": user.id,
            "username": user.username,
            "fullname": user.fullname,
            "photo": user.photo.url if user.photo else None
        }