"""
S3 퍼블릭 버킷 탐지 스크립트
=============================
내 AWS 계정에 있는 모든 S3 버킷을 확인해서,
혹시 실수로 "전체 공개"로 설정된 버킷이 있는지 찾아주는 스크립트예요.

실행 전 준비물:
1. pip install boto3
2. aws configure 로 자격증명 등록 완료
"""

import boto3
from botocore.exceptions import ClientError


def get_s3_client():
    """
    S3 서비스에 접근하기 위한 '연결 통로'를 만드는 함수예요.
    boto3.client("s3")를 호출하면, 컴퓨터에 등록된 AWS 자격증명
    (aws configure로 등록한 것)을 자동으로 찾아서 연결해줘요.
    그래서 코드 안에는 키를 직접 적지 않아도 돼요.
    """
    return boto3.client("s3")


def is_bucket_public(s3_client, bucket_name):
    """
    특정 버킷 하나가 '외부에 공개'되어 있는지 확인하는 함수예요.

    AWS는 버킷이 공개 상태인지 판단해주는 공식 기능을 제공해요:
    get_bucket_policy_status() -> 버킷 정책(Policy) 때문에 공개됐는지 알려줌
    """
    try:
        # AWS에게 "이 버킷, 정책상 공개 상태야?" 라고 물어보는 부분이에요
        response = s3_client.get_bucket_policy_status(Bucket=bucket_name)

        # 응답 안의 IsPublic 값이 True면 진짜로 공개 상태라는 뜻이에요
        return response["PolicyStatus"]["IsPublic"]

    except ClientError as e:
        # 버킷에 정책 자체가 없으면 AWS가 에러를 던져요.
        # 이건 "위험하다"가 아니라 "정책이 아예 없다"는 뜻이에요.
        # (참고: ACL로도 공개될 수 있는데, 이건 다음 버전에서 추가할 예정이에요)
        if e.response["Error"]["Code"] == "NoSuchBucketPolicy":
            return False
        else:
            print(f"  ⚠️ {bucket_name} 확인 중 에러 발생: {e}")
            return None


def scan_all_buckets():
    """
    계정에 있는 모든 S3 버킷을 하나씩 돌면서
    공개 여부를 확인하는 메인 함수예요.
    """
    s3 = get_s3_client()

    # 1. 계정에 있는 모든 버킷 목록 가져오기
    response = s3.list_buckets()
    buckets = response["Buckets"]

    print(f"총 {len(buckets)}개의 버킷을 발견했습니다. 검사를 시작합니다...\n")

    public_buckets = []  # 공개로 확인된 버킷 이름을 모아둘 리스트

    # 2. 버킷을 하나씩 돌면서 검사
    for bucket in buckets:
        name = bucket["Name"]
        is_public = is_bucket_public(s3, name)

        if is_public is True:
            print(f"🚨 위험: '{name}' 버킷이 공개 상태입니다!")
            public_buckets.append(name)
        elif is_public is False:
            print(f"✅ 안전: '{name}' 버킷은 비공개입니다.")
        # is_public이 None이면 에러난 경우라 위에서 이미 출력했어요

    # 3. 최종 결과 요약
    print("\n" + "=" * 40)
    print(f"검사 완료! 공개된 버킷 수: {len(public_buckets)}개")
    if public_buckets:
        print("공개된 버킷 목록:", public_buckets)


# 이 파일을 직접 실행했을 때만 스캔이 시작되도록 하는 부분이에요
# (다른 파일에서 import 할 때는 자동 실행 안 되게 하는 관례예요)
if __name__ == "__main__":
    scan_all_buckets()
