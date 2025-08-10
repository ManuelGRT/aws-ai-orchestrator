output "s3_images_bucket_arn" {
  description = "The ARN of the s3 Bucket"
  value       = aws_s3_bucket.images_bucket.arn
}

output "s3_apigw_waf_bucket_arn" {
  description = "The ARN of the Api Gateway WAF s3 Bucket"
  value = aws_s3_bucket.waf_apigateway_s3_log_bucket.arn
}

output "s3_public_app_bucket_domain_name" {
  description = "The Regional Domain Name of the Public App s3 Bucket"
  value = aws_s3_bucket.s3_bucket_cloudfront.bucket_regional_domain_name
}