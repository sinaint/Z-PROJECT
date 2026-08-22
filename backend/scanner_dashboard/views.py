"""
scanner_dashboard 앱의 view 파일이에요.
사용자가 웹페이지에 접속했을 때 '무슨 일을 할지' 정하는 곳이에요.
"""

from django.shortcuts import render

from .models import ScanResult


def dashboard(request):
    """
    DB에 저장된 최신 스캔 결과를 화면에 보여줘요.
    실제 스캔(+ AI 설명 생성)은 이 화면의 버튼이 호출하는
    POST /api/scan/cloud/, /api/scan/code/ 에서 실행돼요.
    """
    cloud_results = ScanResult.objects.filter(category=ScanResult.Category.CLOUD)[:50]
    code_results = ScanResult.objects.filter(category=ScanResult.Category.CODE)[:50]
    phishing_results = ScanResult.objects.filter(category=ScanResult.Category.PHISHING)[:50]

    context = {
        "cloud_results": cloud_results,
        "code_results": code_results,
        "phishing_results": phishing_results,
        "cloud_total": cloud_results.count(),
        "cloud_risky": sum(1 for r in cloud_results if r.is_risky),
        "code_risky": code_results.count(),
        "phishing_risky": sum(1 for r in phishing_results if r.is_risky),
    }
    return render(request, "scanner_dashboard/dashboard.html", context)
