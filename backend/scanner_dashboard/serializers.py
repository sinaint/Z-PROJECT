from rest_framework import serializers

from .models import ScanResult


class ScanResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanResult
        fields = ["id", "category", "target", "is_risky", "detail", "ai_explanation", "scanned_at"]
