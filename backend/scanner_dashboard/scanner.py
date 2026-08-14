"""
S3 퍼블릭 버킷 스캔 로직
=========================
기존 scan_s3_public.py랑 핵심 로직은 똑같아요.
차이점: print()로 출력하는 대신, 결과를 리스트(list)로 '반환(return)'해요.
그래야 Django 화면(template)에 이 데이터를 넘겨줘서 표로 그릴 수 있거든요.
"""

import boto3
from botocore.exceptions import ClientError


def get_s3_client():
    """S3 서비스에 접근하기 위한 연결 통로를 만드는 함수예요."""
    return boto3.client("s3")


def is_bucket_public(s3_client, bucket_name):
    """
    버킷 하나가 공개 상태인지 확인해요.
    True(공개) / False(비공개) / None(에러로 판단 불가) 중 하나를 반환해요.
    """
    try:
        response = s3_client.get_bucket_policy_status(Bucket=bucket_name)
        return response["PolicyStatus"]["IsPublic"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucketPolicy":
            return False
        else:
            return None


def scan_all_buckets():
    """
    모든 버킷을 스캔해서 결과를 리스트로 반환하는 함수예요.

    반환 형태 예시:
    [
        {"name": "my-bucket-1", "is_public": False},
        {"name": "my-bucket-2", "is_public": True},
    ]

    이렇게 딕셔너리(dict)들의 리스트로 만들어두면,
    Django 템플릿에서 반복문(for)으로 하나씩 꺼내서 표로 그리기 편해요.
    """
    s3 = get_s3_client()
    response = s3.list_buckets()
    buckets = response["Buckets"]

    results = []  # 최종 결과를 담을 리스트

    for bucket in buckets:
        name = bucket["Name"]
        is_public = is_bucket_public(s3, name)
        results.append({
            "name": name,
            "is_public": is_public,
        })

    return results
