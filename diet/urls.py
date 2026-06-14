from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *
from django.conf import settings

urlpatterns = [
    path('tag/search/<str:tag_name>/', TagDietView.as_view()),
    path('tag.<int:id>/', TagSearchView.as_view()),
    path('<str:tag_name>/', DietView.as_view()),
    path('', DietViewPost.as_view()),
    path('save', SaveDietView.as_view()),
    path('save/<int:pk>/', SaveDietPost.as_view()),
    path('popular', PopularView.as_view()),
    path('likes/<int:pk>/', LikeView.as_view()),
    path('today', TodayDietView.as_view()),
    path('analyze', AnalyzeTodayDietView.as_view()),
    path('reservation/<str:date>/', DayDietDetailView.as_view()),
    path('recommends', RecommendDietView.as_view()),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)