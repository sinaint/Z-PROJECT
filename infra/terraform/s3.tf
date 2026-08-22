# 테스트용 S3 버킷
# ------------------------------------------------------------
# 이름이 전 세계에서 겹치면 안 되는 게 S3 버킷 규칙이라,
# random_id로 뒤에 랜덤 문자열을 붙여요.

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "test" {
  bucket = "${var.bucket_name_prefix}-${random_id.bucket_suffix.hex}"

  tags = {
    Project = "Z-PROJECT"
    Purpose = "scanner-test"
  }
}

# "모든 퍼블릭 액세스 차단" 설정이에요.
# enable_public_access가 false(기본값)면 전부 차단(true)돼서 안전한 상태를 유지해요.
resource "aws_s3_bucket_public_access_block" "test" {
  bucket = aws_s3_bucket.test.id

  block_public_acls       = !var.enable_public_access
  block_public_policy     = !var.enable_public_access
  ignore_public_acls      = !var.enable_public_access
  restrict_public_buckets = !var.enable_public_access
}

# enable_public_access가 true일 때만, 콘솔에서 직접 만들었던 것과 똑같은
# "누구나 읽기 가능" 정책을 붙여요. (스캐너가 이걸 잡아내는지 테스트하는 용도)
resource "aws_s3_bucket_policy" "public_read" {
  count = var.enable_public_access ? 1 : 0

  bucket = aws_s3_bucket.test.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.test.arn}/*"
      }
    ]
  })

  # 퍼블릭 액세스 차단이 먼저 풀려있어야 정책이 실제로 적용돼요.
  depends_on = [aws_s3_bucket_public_access_block.test]
}
