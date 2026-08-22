from django.contrib import admin
from django.urls import path, include  # include를 새로 import 해야 해요

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # 로그인/로그아웃 (accounts/login/, accounts/logout/)
    path('', include('scanner_dashboard.urls')),   # 이 한 줄을 추가
]
