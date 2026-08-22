variable "aws_region" {
  description = "리소스를 만들 AWS 리전이에요."
  type        = string
  default     = "ap-northeast-2"
}

variable "bucket_name_prefix" {
  description = "테스트용 S3 버킷 이름의 앞부분이에요. 뒤에 랜덤 문자열이 자동으로 붙어서 이름이 겹치지 않아요."
  type        = string
  default     = "zproject-test-bucket"
}

variable "enable_public_access" {
  description = <<-EOT
    true로 바꾸면 S3 버킷을 일부러 퍼블릭으로 열어서,
    대시보드의 "클라우드 스캔"이 이걸 위험으로 잡아내는지 테스트할 수 있어요.
    평소엔 false로 두세요 (기본값).
  EOT
  type        = bool
  default     = false
}

variable "enable_open_ssh" {
  description = <<-EOT
    true로 바꾸면 보안 그룹에 0.0.0.0/0으로 SSH(22번 포트)를 일부러 열어서
    스캐너 테스트를 할 수 있어요. 평소엔 false로 두세요 (기본값).
  EOT
  type        = bool
  default     = false
}
