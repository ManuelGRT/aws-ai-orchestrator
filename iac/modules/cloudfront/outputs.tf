output "cloudfront_oai_arn" {
  description = "Cloudfront OAI Arn"
  value       = aws_cloudfront_origin_access_identity.s3_oai.iam_arn
}