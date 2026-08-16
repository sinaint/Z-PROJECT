"""
frontend/(React)가 붙을 수 있도록 JSON으로 응답하는 API예요.
GET  /api/scan-results/  : 저장된 스캔 결과 조회
POST /api/scan/cloud/    : S3 스캔 실행 + AI 설명 생성 + 저장
POST /api/scan/code/     : 코드 시크릿 스캔 실행 + AI 설명 생성 + 저장
"""

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import ai_explainer, code_scanner
from .models import ScanResult
from .scanner import scan_all_buckets
from .serializers import ScanResultSerializer


@api_view(["GET"])
def list_scan_results(request):
    """저장된 스캔 결과를 최신순으로 반환해요. ?category=cloud|code|phishing 로 필터링 가능해요."""
    queryset = ScanResult.objects.all()
    category = request.query_params.get("category")
    if category:
        queryset = queryset.filter(category=category)
    return Response(ScanResultSerializer(queryset, many=True).data)


@api_view(["POST"])
def run_cloud_scan(request):
    """S3 버킷을 스캔하고, 결과마다 AI 설명을 붙여서 DB에 저장해요."""
    raw_results = scan_all_buckets()
    saved = []
    for item in raw_results:
        is_risky = bool(item["is_public"])
        explanation = ai_explainer.explain_finding(
            category=ScanResult.Category.CLOUD, target=item["name"], is_risky=is_risky,
        )
        saved.append(ScanResult.objects.create(
            category=ScanResult.Category.CLOUD,
            target=item["name"],
            is_risky=is_risky,
            ai_explanation=explanation,
        ))
    return Response(ScanResultSerializer(saved, many=True).data)


@api_view(["POST"])
def run_code_scan(request):
    """소스코드 안 하드코딩된 시크릿을 스캔하고, AI 설명을 붙여서 DB에 저장해요."""
    findings = code_scanner.scan_codebase(str(settings.BASE_DIR))
    saved = []
    for finding in findings:
        detail = f"{finding['file']}:{finding['line']} ({finding['pattern_name']}) - {finding['snippet']}"
        explanation = ai_explainer.explain_finding(
            category=ScanResult.Category.CODE, target=finding["file"], is_risky=True, detail=detail,
        )
        saved.append(ScanResult.objects.create(
            category=ScanResult.Category.CODE,
            target=finding["file"],
            is_risky=True,
            detail=detail,
            ai_explanation=explanation,
        ))
    return Response(ScanResultSerializer(saved, many=True).data)
