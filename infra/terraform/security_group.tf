# 테스트용 보안 그룹
# ------------------------------------------------------------
# 계정의 기본(default) VPC 안에 만들어요. 별도로 VPC를 새로 만들 필요는 없어요.

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "test" {
  name        = "zproject-test-sg"
  description = "Z-PROJECT 스캐너 테스트용 보안 그룹"
  vpc_id      = data.aws_vpc.default.id

  tags = {
    Project = "Z-PROJECT"
    Purpose = "scanner-test"
  }
}

# enable_open_ssh가 true일 때만, 0.0.0.0/0에 SSH(22)를 열어요.
# 이게 바로 대시보드의 "클라우드 스캔"이 위험으로 잡아내야 하는 규칙이에요.
resource "aws_security_group_rule" "open_ssh" {
  count = var.enable_open_ssh ? 1 : 0

  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.test.id
  description       = "TEST ONLY: 스캐너 탐지 테스트용 - 0.0.0.0/0에 열린 SSH"
}
