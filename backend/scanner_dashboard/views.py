"""
scanner_dashboard 앱의 view 파일이에요.
사용자가 웹페이지에 접속했을 때 '무슨 일을 할지' 정하는 곳이에요.
"""

from django.shortcuts import render
from .scanner import scan_all_buckets


def dashboard(request):
    """
    누군가 대시보드 페이지에 접속하면 실행되는 함수예요.

    흐름:
    1. scan_all_buckets()를 호출해서 실제로 AWS를 스캔해요
    2. 결과 중 '공개된 버킷' 개수를 따로 세어요 (요약 정보용)
    3. 결과를 dashboard.html 템플릿에 넘겨서 화면에 그려요
    """
    results = scan_all_buckets()

    # 리스트 안에서 is_public이 True인 것만 세는 부분이에요
    public_count = sum(1 for r in results if r["is_public"] is True)

    # context는 템플릿(html)에 넘겨줄 데이터 꾸러미예요.
    # 여기 담은 키(key) 이름 그대로 html에서 {{ 이름 }} 형태로 꺼내 쓸 수 있어요.
    context = {
        "results": results,
        "total_count": len(results),
        "public_count": public_count,
    }

    return render(request, "scanner_dashboard/dashboard.html", context)
