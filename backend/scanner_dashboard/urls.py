"""
scanner_dashboard 앱 전용 URL 설정이에요.
"어떤 주소로 들어오면 어떤 view 함수를 실행할지" 정하는 파일이에요.
"""

from django.urls import path

from . import api_views, views

urlpatterns = [
    # 빈 경로("")로 접속하면 views.py의 dashboard 함수를 실행해요
    path("", views.dashboard, name="dashboard"),

    # REST API (프론트엔드 React 연동용)
    path("api/scan-results/", api_views.list_scan_results, name="api-scan-results"),
    path("api/scan/cloud/", api_views.run_cloud_scan, name="api-scan-cloud"),
    path("api/scan/code/", api_views.run_code_scan, name="api-scan-code"),
    path("api/scan/phishing/", api_views.run_phishing_scan, name="api-scan-phishing"),
]
