from rest_framework import serializers
from .models import *

class DietSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Diet
        fields = ['id','name','text','image','tags', 'kcal', 'carbohydrate', 'protein', 'fat', 'dietary_fiber', 'calcium', 'sodium', 'ingredients','user']

class DietResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = ['id','name','text','tags', 'kcal', 'carbohydrate', 'protein', 'fat', 'dietary_fiber', 'calcium', 'sodium', 'ingredients','user', 'share_score', 'likes', 'image']

    def to_representation(self, instance):
        if instance is None:
            return None  # 또는 {}, {'diet_type': None} 등
        return super().to_representation(instance)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class SaveDietSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = SaveDiet
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class DayDietSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DayDiet
        fields = ['diet_type','diet','user']

class DayDietSerializerWithDay(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    day = serializers.DateField()

    class Meta:
        model = DayDiet
        fields = ['diet_type', 'diet', 'user', 'day']