from django.urls import path, include
from .views import *

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('my_page/', MyPageView.as_view(),),
    path('tags/<str:tag_name>', TagUserDetailView.as_view(),),
    path('tags/', UserTagView.as_view(),),
]