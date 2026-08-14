"""
scanner_dashboard 앱 전용 URL 설정이에요.
"어떤 주소로 들어오면 어떤 view 함수를 실행할지" 정하는 파일이에요.
"""

from django.urls import path
from . import views

urlpatterns = [
    # 빈 경로("")로 접속하면 views.py의 dashboard 함수를 실행해요
    path("", views.dashboard, name="dashboard"),
]
