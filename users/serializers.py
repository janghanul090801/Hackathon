from rest_framework import serializers
from .models import User, UserTag
from dj_rest_auth.registration.serializers import RegisterSerializer

class UserTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTag
        fields = ('id', 'name')

class CustomRegisterSerializer(RegisterSerializer):
    name = serializers.CharField(max_length=30)
    tags = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    gender = serializers.BooleanField(default=False)
    age = serializers.IntegerField(default=0)

    _has_phone_field = False
    username = None

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['name'] = self.validated_data.get('name', '')
        data['tags'] = self.validated_data.get('tags', [])
        data['gender'] = self.validated_data.get('gender', False)
        data['age'] = self.validated_data.get('age', 0)
        return data

    def save(self, request):
        user = super().save(request)
        user.name = self.validated_data.get('name')
        user.gender = self.validated_data.get('gender')
        user.age = self.validated_data.get('age')
        user.save()

        tag_ids = self.validated_data.get('tags', [])
        tags = UserTag.objects.filter(id__in=tag_ids)
        user.tags.set(tags)

        return user

class CustomUserSerializer(serializers.ModelSerializer):
    username = None
    class Meta:
        model = User
        fields = ('id', 'email', 'name')

class MyPageSerializer(RegisterSerializer):
    _has_phone_field = False

    class Meta:
        model = User
        fields = ['email','name','created_at']

from dj_rest_auth.serializers import JWTSerializer, LoginSerializer


class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

class CustomJWTSerializer(JWTSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['name'] = self.user.name
        data['email'] = self.user.email

        return data
