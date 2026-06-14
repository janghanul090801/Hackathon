
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


# Create your models here.

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

class Diet(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    text = models.TextField()
    image = models.ImageField(upload_to='images/')
    kcal = models.IntegerField(default=0)
    # 탄수화물
    carbohydrate = models.IntegerField(default=0,validators=[MinValueValidator(0),])
    # 단백질
    protein = models.IntegerField(default=0,validators=[MinValueValidator(0),])
    # 지방
    fat = models.IntegerField(default=0,validators=[MinValueValidator(0),])
    # 식이섬유
    dietary_fiber = models.IntegerField(default=0,validators=[MinValueValidator(0),])
    # 칼슘
    calcium = models.IntegerField(default=0,validators=[MinValueValidator(0),])
    # 나트륨
    sodium = models.IntegerField(default=0,validators=[MinValueValidator(0),])
    ingredients = models.TextField()
    share_score = models.BigIntegerField(default=0)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

class Like(models.Model):
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class DayDiet(models.Model):
    id = models.AutoField(primary_key=True)
    DIET_TYPE_CHOICES = [
        ('breakfast', 'breakfast'),
        ('lunch', 'lunch'),
        ('dinner', 'dinner'),
        ('desert', 'desert'),
    ]
    diet_type = models.CharField(max_length=100, choices=DIET_TYPE_CHOICES)
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE)
    day = models.DateField(default=timezone.now)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

class SaveDiet(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE)
