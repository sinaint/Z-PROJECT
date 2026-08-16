from django.db import models


class ScanResult(models.Model):
    """
    스캔 결과 하나를 저장하는 모델이에요.
    클라우드(S3 등), 코드, 피싱 세 영역 스캔 결과를 한 테이블에서 같이 관리해요.
    """

    class Category(models.TextChoices):
        CLOUD = "cloud", "클라우드 인프라"
        CODE = "code", "코드"
        PHISHING = "phishing", "피싱"

    category = models.CharField(max_length=20, choices=Category.choices)
    target = models.CharField(max_length=500)  # 예: 버킷 이름, 파일 경로
    is_risky = models.BooleanField()
    detail = models.TextField(blank=True)  # 원본 스캔 정보 (매칭된 줄 등)
    ai_explanation = models.TextField(blank=True)  # LLM이 생성한 설명/조치법
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scanned_at"]

    def __str__(self):
        return f"[{self.category}] {self.target}"
