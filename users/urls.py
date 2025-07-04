from django.urls import path, include

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),               # 로그인, 로그아웃, 비밀번호 변경 등
    path('auth/registration/', include('dj_rest_auth.registration.urls')),  # 회원가입 관련
]