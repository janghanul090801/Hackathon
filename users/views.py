from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import UserTag
from .serializers import MyPageSerializer, UserTagSerializer
from rest_framework.response import Response

# Create your views here.

class MyPageView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = MyPageSerializer(user)

        return Response(serializer.data)

class TagUserDetailView(APIView):

    @swagger_auto_schema(tags=['태그 정보 반환 근데 유저인'])
    def get(self, request, tag_name: str):
        tag = UserTag.objects.get_or_create(name=tag_name)[0]
        serializer = UserTagSerializer(tag)
        return Response(serializer.data)

class UserTagView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = request.user
        tags = UserTag.objects.filter(user=user)
        serializer = UserTagSerializer(tags, many=True)
        return Response(serializer.data)

