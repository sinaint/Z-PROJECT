output "bucket_name" {
  description = "생성된 테스트 S3 버킷 이름 (Django 스캐너 테스트에 사용)"
  value       = aws_s3_bucket.test.bucket
}

output "security_group_id" {
  description = "생성된 테스트 보안 그룹 ID (Django 스캐너 테스트에 사용)"
  value       = aws_security_group.test.id
}
