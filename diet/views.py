from datetime import datetime, date
from functools import reduce
from random import sample

from django.db.models import Count, Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
import uuid
from .models import Diet, Tag
from .serializers import *
from rest_framework import mixins, generics, viewsets, status



# Create your views here.

class TagDietView(APIView):
    @swagger_auto_schema(tags=['태그 정보 반환'])
    def get(self, request, tag_name: str):
        tag = Tag.objects.get_or_create(name=tag_name)[0]
        serializer = TagSerializer(tag)
        return Response(serializer.data)

class TagSearchView(APIView):
    @swagger_auto_schema(tags=['태그 아이디 to 태그 정보'])
    def get(self, request, id: int):
        tag = Tag.objects.filter(id=id).first()
        if tag is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TagSerializer(tag)
        return Response(serializer.data)



class DietView(
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Diet.objects.all()
    serializer_class = DietSerializer

    # 페이지네이션 추가 필요
    @swagger_auto_schema(tags=['태그 검색 근데 입력을 [<태그>,<태그>] 이케 해야함'])
    def get(self, request, tag_name: str = None):
        diets = Diet.objects.all()
        if tag_name:
            for tag in tag_name.split(','):
                diets = diets.filter(tags__name=tag)
            serializer = DietResponseSerializer(diets, many=True)
            return Response(serializer.data)
        else:
            diets = Diet.objects.all()
            serializer = DietResponseSerializer(diets, many=True)
            return Response(serializer.data)

class DietViewPost(
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    serializer_class = DietSerializer
    queryset = Diet.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(tags=['내 식단 반환'])
    def get(self, request):
        diets = Diet.objects.filter(user=self.request.user)
        serializer = DietResponseSerializer(diets, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['식단 post'])
    def post(self, request, **kwargs):
        data = request.data
        data['image'].name = uuid.uuid4().hex+'.png'
        serializer = DietSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SaveDietView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['지금 있는 saved diet 반환'])
    def get(self, request):
        saves = SaveDiet.objects.filter(user=self.request.user)
        diets = []
        for save in saves:
            diets.append(save.diet)
        serializer = DietResponseSerializer(diets, many=True)
        return Response(serializer.data)

class SaveDietPost(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['식단 save 하기'])
    def post(self, request, pk: int):
        diet = Diet.objects.filter(id=pk).first()
        before = SaveDiet.objects.filter(user=request.user, diet=diet).first()
        if before:
            return Response({'error': 'Diet already saved'})

        SaveDiet.objects.create(user=self.request.user, diet=diet)
        diet.share_score += 1
        diet.save()
        return Response({'message': 'Diet saved'})

class PopularView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(tags=['가장 핫한 4개'])
    def get(self, request):
        from datetime import timedelta
        from django.utils import timezone

        diets = (Diet.objects
                 .filter(likes__created_at__gte=(timezone.now() - timedelta(days=7)))
                 .annotate(recent_likes=Count('likes', filter=models.Q(likes__created_at__gte=(timezone.now() - timedelta(days=7)))))
                 .order_by('-recent_likes')
                 .all()[:4])

        serializer = DietResponseSerializer(diets, many=True)
        return Response(serializer.data)

class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        diet = Diet.objects.get(id=pk)
        likes = diet.likes.count()

        return Response({"likes":likes})

    def post(self, request, pk: int):
        diets = Diet.objects.get(id=pk)
        like = Like.objects.filter(diet=diets, user=request.user).first()
        if like:
            return Response({'error': 'Diet already liked'})
        Like.objects.create(diet=diets, user=request.user)
        return Response({'message': 'Diet liked'})

class TodayDietView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["오늘 식단 리턴"])
    def get(self, request):
        today = date.today()
        day_diets = DayDiet.objects.filter(day=today, user=request.user)

        meal_types = ['breakfast', 'lunch', 'dinner', 'desert']
        diets = []

        for meal in meal_types:
            day_diet = day_diets.filter(diet_type=meal).first()
            if day_diet:
                try:
                    diet = day_diet.diet  # 이 라인에서 DoesNotExist 터질 수 있음
                    diets.append(diet)
                except Diet.DoesNotExist:
                    pass  # 연결된 diet가 없으면 그냥 넘김

        serializer = DietResponseSerializer(diets, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['today diet에 넣는거'], request_body=DayDietSerializer)
    def post(self, request):
        serializer = DayDietSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def make_ratio(carb_g, protein_g, fat_g, total_kcal):
    carb_kcal = carb_g * 4
    protein_kcal = protein_g * 4
    fat_kcal = fat_g * 9

    carb_percent = round(carb_kcal / total_kcal * 100, 1)
    protein_percent = round(protein_kcal / total_kcal * 100, 1)
    fat_percent = round(fat_kcal / total_kcal * 100, 1)

    return {
        "carb_percent": carb_percent,
        "protein_percent": protein_percent,
        "fat_percent": fat_percent
    }

class AnalyzeTodayDietView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nutrient = {
            "kcal":0,
            "carbohydrates": 0,
            "protein": 0,
            "fat" : 0,
            "dietary_fiber": 0,
            "calcium":0,
            "sodium":0
        }
        for day_diet in DayDiet.objects.filter(day=datetime.today()).filter(user=self.request.user):
            nutrient["kcal"] += day_diet.diet.kcal
            nutrient["carbohydrates"] += day_diet.diet.carbohydrate
            nutrient["protein"] += day_diet.diet.protein
            nutrient["fat"] += day_diet.diet.fat
            nutrient["dietary_fiber"] += day_diet.diet.dietary_fiber
            nutrient["calcium"] += day_diet.diet.calcium
            nutrient["sodium"] += day_diet.diet.sodium

        tags = request.user.tags.all()

        response_str = {
            "kcal": "",
            "carb": "",
            "protein": "",
            "fat": "",
            "dietary_fiber": "",
            "calcium": "",
            "sodium": ""
        }

        if request.user.gender:
            if 2500 > nutrient["kcal"]:
                response_str["kcal"] = "칼로리가 너무 작아요"
            elif 3000 < nutrient["kcal"]:
                response_str["kcal"] = "칼로리가 너무 많아요"
            else:
                response_str["kcal"] = "칼로리가 적당해요"
        else:
            if 2000 > nutrient["kcal"]:
                response_str["kcal"] = "칼로리가 너무 작아요"
            elif 2400 < nutrient["kcal"]:
                response_str["kcal"] = "칼로리가 너무 많아요"
            else:
                response_str["kcal"] = "칼로리가 적당해요"

        ratio = make_ratio(nutrient["carbohydrates"], nutrient["protein"], nutrient["fat"], nutrient["kcal"])
        if 30 > ratio["carb_percent"]:
            response_str["carb"] = "탄수화물이 너무 적어요"
        elif 50 < ratio["carb_percent"]:
            response_str["carb"] = "탄수화물이 너무 많아요"
        else:
            response_str["carb"] = "탄수화물이 적당해요"

        if 30 > ratio["protein_percent"]:
            response_str["protein"] = "단백질이 너무 적어요"
        elif 50 < ratio["protein_percent"]:
            response_str["protein"] = "단백질이 너무 많아요"
        else:
            response_str["protein"] = "단백질이 적당해요"

        if 10 > ratio["fat_percent"]:
            response_str["fat"] = "지방이 너무 적어요"
        elif 30 < ratio["fat_percent"]:
            response_str["fat"] = "지방이 너무 많아요"
        else:
            response_str["fat"] = "지방이 적당해요"

        if 25 > nutrient["dietary_fiber"]:
            response_str["dietary_fiber"] = "식이섬유가 너무 적어요"
        else:
            response_str["dietary_fiber"] = '식이섬유가 적당해요'

        if nutrient["calcium"] < 700:
            response_str["calcium"] = "칼슘이 너무 적어요"
        elif nutrient["calcium"] > 1000:
            response_str["calcium"] = "칼슘이 너무 많아요"
        else:
            response_str["calcium"] = "칼슘이 적당해요"

        if nutrient["sodium"] > 4000:
            response_str["sodium"] = "나트륨이 너무 많아요"
        else:
            response_str["sodium"] = "나트륨이 적당해요"

        if "health" in tags:
            if 40 > ratio["carb_percent"]:
                response_str["carb"] = "탄수화물이 너무 적어요"
            elif 60 < ratio["carb_percent"]:
                response_str["carb"] = "탄수화물이 너무 많아요"
            else:
                response_str["carb"] = "탄수화물이 적당해요"

            if 20 > ratio["protein_percent"]:
                response_str["protein"] = "단백질이 너무 적어요"
            elif 40 < ratio["protein_percent"]:
                response_str["protein"] = "단백질이 너무 많아요"
            else:
                response_str["protein"] = "단백질이 적당해요"

        # 당뇨
        if 'diabetes' in tags:
            if 60 < ratio["carb_percent"]:
                response_str["carb"] = "탄수화물이 너무 많아요"
            else:
                response_str["carb"] = "탄수화물이 적당해요"

            if 45 > nutrient["dietary_fiber"]:
                response_str["dietary_fiber"] = "식이섬유가 너무 적어요"
            else:
                response_str["dietary_fiber"] = '식이섬유가 적당해요'

        # 골다공증
        if 'osteoporosis' in tags:
            if 1000 > nutrient['calcium']:
                response_str['calcium'] = "칼슘이 너무 적어요"
            elif 1500 < nutrient['calcium']:
                response_str['calcium'] = '칼슘이 너무 많아요'
            else:
                response_str['calcium'] = '칼슘이 적당해요'

        # 고혈압
        if 'high_blood_pressure' in tags:
            if 2000 < nutrient["sodium"]:
                response_str["sodium"] = "나트륨이 너무 많아요"
            else:
                response_str["sodium"] = "나트륨이 적당해요"


        return Response(response_str)

class RecommendDietView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("fjdlkaljkldalk")
        diets = (Diet.objects
            .annotate(
                match_score=Count(
                    'tags',
                    filter=Q(tags__in=request.user.tags.values_list('id', flat=True)),
                )
            )
            .filter(match_score__gt=0)
            .order_by('-match_score')
                  )

        diets_list = list(diets)

        if not diets_list:
            diets_list = list(Diet.objects.all())

        limit = 16
        if len(diets_list) <= limit:
            selected_diets = diets_list
        else:
            selected_diets = sample(diets_list, limit)

        serializer = DietSerializer(selected_diets, many=True)
        return Response(serializer.data)

class DayDietDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Y-M-D 형식으로 넣으셈"])
    def get(self, request, date:str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
        day_diets = DayDiet.objects.filter(day=date)
        if day_diets.exists():
            diets = [
                day_diets.filter(diet_type='breakfast').first(),
                day_diets.filter(diet_type='lunch').first(),
                day_diets.filter(diet_type='dinner').first(),
                day_diets.filter(diet_type='desert').first()
            ]

            results = []
            for diet in diets:
                if diet is not None:
                    results.append(DietResponseSerializer(diet.diet).data)
                else:
                    results.append(None)

            return Response(results)
        return Response({"message":"Diet Not Found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(tags=['Y-M-D 형식으로 넣으셈'],request_body=DayDietSerializerWithDay)
    def post(self, request, date:str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
        data = request.data.copy()
        data['day'] = date
        serializer = DayDietSerializerWithDay(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)