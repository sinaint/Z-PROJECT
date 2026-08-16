"""
frontend/(React)가 붙을 수 있도록 JSON으로 응답하는 API예요.
GET  /api/scan-results/  : 저장된 스캔 결과 조회
POST /api/scan/cloud/    : S3 + IAM + 보안 그룹 스캔 실행 + AI 설명 생성 + 저장
POST /api/scan/code/     : 코드 시크릿 스캔 실행 + AI 설명 생성 + 저장
"""

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import ai_explainer, code_scanner
from .models import ScanResult
from .scanner import scan_all_buckets, scan_iam_users, scan_security_groups
from .serializers import ScanResultSerializer


def _save_finding(category, target, is_risky, detail=""):
    """스캔 결과 하나를 AI 설명까지 붙여서 DB에 저장하는 공통 헬퍼예요."""
    explanation = ai_explainer.explain_finding(
        category=category, target=target, is_risky=is_risky, detail=detail,
    )
    return ScanResult.objects.create(
        category=category, target=target, is_risky=is_risky,
        detail=detail, ai_explanation=explanation,
    )


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
    """S3 버킷 + IAM 사용자 + 보안 그룹을 스캔하고, 결과마다 AI 설명을 붙여서 DB에 저장해요."""
    saved = []

    # 1) S3 퍼블릭 버킷
    for item in scan_all_buckets():
        saved.append(_save_finding(
            category=ScanResult.Category.CLOUD,
            target=f"S3 버킷: {item['name']}",
            is_risky=bool(item["is_public"]),
        ))

    # 2) IAM 사용자 (과도한 권한 / MFA 미설정 / 오래된 Access Key)
    for item in scan_iam_users():
        saved.append(_save_finding(
            category=ScanResult.Category.CLOUD,
            target=f"IAM 사용자: {item['user']}",
            is_risky=item["is_risky"],
            detail=", ".join(item["reasons"]),
        ))

    # 3) 보안 그룹 (0.0.0.0/0에 열린 민감 포트)
    for item in scan_security_groups():
        saved.append(_save_finding(
            category=ScanResult.Category.CLOUD,
            target=f"보안 그룹: {item['group_name'] or item['group_id']}",
            is_risky=item["is_risky"],
            detail=f"{item['port']} 포트가 {item['cidr']}에 열려있음",
        ))

    return Response(ScanResultSerializer(saved, many=True).data)


@api_view(["POST"])
def run_code_scan(request):
    """소스코드 안 하드코딩된 시크릿을 스캔하고, AI 설명을 붙여서 DB에 저장해요."""
    findings = code_scanner.scan_codebase(str(settings.BASE_DIR))
    saved = []
    for finding in findings:
        detail = f"{finding['file']}:{finding['line']} ({finding['pattern_name']}) - {finding['snippet']}"
        saved.append(_save_finding(
            category=ScanResult.Category.CODE,
            target=finding["file"],
            is_risky=True,
            detail=detail,
        ))
    return Response(ScanResultSerializer(saved, many=True).data)
