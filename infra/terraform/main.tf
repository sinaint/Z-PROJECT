# Z-PROJECT 스캐너 테스트용 AWS 리소스
# =========================================
# 이 폴더는 실제로 서비스를 운영하는 인프라가 아니라,
# 백엔드 스캐너(S3/보안그룹 탐지)가 잘 동작하는지 확인하기 위한
# "일부러 취약하게 만들어볼 수 있는" 테스트 리소스예요.
#
# 사용법:
#   terraform init
#   terraform plan
#   terraform apply
#
# 다 확인했으면 반드시 정리하세요:
#   terraform destroy

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
