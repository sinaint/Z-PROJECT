# infra/terraform

Z-PROJECT 스캐너(S3 / 보안 그룹 탐지)가 잘 동작하는지 테스트하기 위한
**테스트 전용** AWS 리소스예요. 실제 서비스 인프라가 아닙니다.

## 사전 준비

1. [Terraform](https://developer.hashicorp.com/terraform/downloads) 설치
2. AWS 자격증명 준비
   - 이 코드는 S3 버킷, 보안 그룹을 **생성/삭제**해요.
   - `backend/scanner_dashboard`가 쓰는 `zproject-scanner` 계정은 **읽기 전용**이라 이 작업엔 권한이 부족해요.
   - 리소스 생성/삭제 권한이 있는 별도 계정(또는 profile)으로 실행하세요.
     ```bash
     export AWS_PROFILE=관리자권한있는-profile-이름
     # 또는
     terraform apply -var-file=... # provider에 profile 지정도 가능
     ```

## 사용법

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

기본값(`enable_public_access=false`, `enable_open_ssh=false`)으로 실행하면
**안전한 상태**(퍼블릭 접근 차단, SSH 안 열림)의 S3 버킷 + 보안 그룹만 생성돼요.

## 스캐너가 위험을 잡아내는지 테스트하려면

```bash
# 일부러 취약하게 만들기
terraform apply -var="enable_public_access=true" -var="enable_open_ssh=true"

# Django 대시보드에서 "클라우드 스캔 실행" 버튼을 눌러서
# 방금 만든 버킷/보안 그룹이 위험으로 잡히는지 확인

# 확인 끝났으면 원래대로(안전한 상태)로 되돌리기
terraform apply
```

## 다 썼으면 꼭 정리하세요

```bash
terraform destroy
```

리소스를 계속 켜두면 실제 AWS 계정에 불필요한 공개 리소스가 남아있게 됩니다.
`*.tfstate` 파일은 `.gitignore`에 이미 포함되어 있어 커밋되지 않아요 (민감정보 포함 가능).
