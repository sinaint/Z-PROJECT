"""
클라우드(AWS) 스캔 로직
=========================
S3 퍼블릭 버킷 / IAM 사용자 / 보안 그룹(Security Group), 세 가지를 점검해요.
전부 print() 대신 결과를 리스트(list)로 '반환(return)'해요.
그래야 Django 화면(template)에 이 데이터를 넘겨줘서 표로 그릴 수 있거든요.
"""

from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

# IAM 사용자한테 이 정책이 직접 붙어있으면 "모든 권한"을 가진 것과 같아요.
ADMIN_POLICY_ARN = "arn:aws:iam::aws:policy/AdministratorAccess"

# Access Key는 이 일수(90일)보다 오래되면 교체(rotate)를 권장해요.
ACCESS_KEY_MAX_AGE_DAYS = 90

# 인터넷 전체를 뜻하는 CIDR이에요. 이 대역에 열려있으면 누구나 접근을 시도할 수 있어요.
OPEN_CIDRS = {"0.0.0.0/0", "::/0"}

# 보안 그룹에서 열려있으면 특히 위험한 포트들이에요.
SENSITIVE_PORTS = {
    22: "SSH",
    3389: "RDP",
    3306: "MySQL",
    5432: "PostgreSQL",
    27017: "MongoDB",
}


def get_s3_client():
    """S3 서비스에 접근하기 위한 연결 통로를 만드는 함수예요."""
    return boto3.client("s3")


def get_iam_client():
    """IAM 서비스에 접근하기 위한 연결 통로를 만드는 함수예요."""
    return boto3.client("iam")


def get_ec2_client():
    """EC2(보안 그룹 포함) 서비스에 접근하기 위한 연결 통로를 만드는 함수예요."""
    return boto3.client("ec2")


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


def scan_iam_users():
    """
    IAM 사용자 한 명 한 명을 점검해서 위험 요소가 있는지 찾아요.
    - AdministratorAccess처럼 과도한 권한이 직접 붙어있는지
    - MFA(다단계 인증)가 꺼져있는지
    - Access Key가 90일 넘게 오래됐는지

    반환 형태 예시:
    [
        {"user": "alice", "is_risky": True, "reasons": ["MFA(다단계 인증)가 설정되어 있지 않음"]},
        {"user": "bob", "is_risky": False, "reasons": []},
    ]
    """
    iam = get_iam_client()
    results = []

    paginator = iam.get_paginator("list_users")
    for page in paginator.paginate():
        for user in page["Users"]:
            username = user["UserName"]
            reasons = []  # 이 사용자에게서 발견된 위험 사유들을 담을 리스트

            # 1) 과도한 권한(AdministratorAccess)이 직접 연결되어 있는지 확인
            attached = iam.list_attached_user_policies(UserName=username)["AttachedPolicies"]
            if any(policy["PolicyArn"] == ADMIN_POLICY_ARN for policy in attached):
                reasons.append("AdministratorAccess 정책이 직접 연결되어 있음")

            # 2) MFA(다단계 인증) 등록 여부 확인
            mfa_devices = iam.list_mfa_devices(UserName=username)["MFADevices"]
            if not mfa_devices:
                reasons.append("MFA(다단계 인증)가 설정되어 있지 않음")

            # 3) 활성화된 Access Key가 너무 오래되지 않았는지 확인
            access_keys = iam.list_access_keys(UserName=username)["AccessKeyMetadata"]
            for key in access_keys:
                if key["Status"] != "Active":
                    continue
                age_days = (datetime.now(timezone.utc) - key["CreateDate"]).days
                if age_days > ACCESS_KEY_MAX_AGE_DAYS:
                    reasons.append(f"Access Key({key['AccessKeyId']})가 생성된 지 {age_days}일 지남 (교체 권장)")

            results.append({
                "user": username,
                "is_risky": bool(reasons),
                "reasons": reasons,
            })

    return results


def scan_security_groups():
    """
    보안 그룹(Security Group)의 인바운드 규칙 중, 인터넷 전체(0.0.0.0/0, ::/0)에
    민감한 포트(SSH, RDP, DB 포트 등)가 열려 있는 규칙을 찾아요.

    반환 형태 예시:
    [
        {"group_id": "sg-123", "group_name": "web-sg", "port": "22/SSH",
         "cidr": "0.0.0.0/0", "is_risky": True},
    ]
    """
    ec2 = get_ec2_client()
    results = []

    paginator = ec2.get_paginator("describe_security_groups")
    for page in paginator.paginate():
        for group in page["SecurityGroups"]:
            for rule in group.get("IpPermissions", []):
                # 이 규칙이 인터넷 전체(0.0.0.0/0 또는 ::/0)에 열려있는지 확인
                open_cidrs = [r["CidrIp"] for r in rule.get("IpRanges", []) if r.get("CidrIp") in OPEN_CIDRS]
                open_cidrs += [r["CidrIpv6"] for r in rule.get("Ipv6Ranges", []) if r.get("CidrIpv6") in OPEN_CIDRS]
                if not open_cidrs:
                    continue

                cidr_text = ", ".join(sorted(set(open_cidrs)))
                from_port = rule.get("FromPort")
                to_port = rule.get("ToPort")

                # IpProtocol이 "-1"이면 "모든 프로토콜/모든 포트 허용"이라는 뜻이에요.
                if rule.get("IpProtocol") == "-1":
                    results.append({
                        "group_id": group["GroupId"],
                        "group_name": group.get("GroupName", ""),
                        "port": "전체 포트",
                        "cidr": cidr_text,
                        "is_risky": True,
                    })
                    continue

                for port, label in SENSITIVE_PORTS.items():
                    if from_port is not None and to_port is not None and from_port <= port <= to_port:
                        results.append({
                            "group_id": group["GroupId"],
                            "group_name": group.get("GroupName", ""),
                            "port": f"{port}/{label}",
                            "cidr": cidr_text,
                            "is_risky": True,
                        })

    return results
