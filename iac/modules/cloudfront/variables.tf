/*
variable "waf_acl_arn" {
  description = "ARN of the WAF ACL"
  type        = string
}
*/

variable "s3_public_app_bucket_regional_domain_name" {
  description = "The Regional Domain Name of the Public App s3 Bucket"
  type        = string  
}

variable "public_alternate_domain_name" {
  description = "Name of the Public Alternate Domain Name"
  type        = string  
}

variable "public_acm_certificate_arn" {
  description = "ARN of the Public ACM Certificate"
  type        = string  
}

variable "s3_cloudfront_log_bucket_domain_name" {
  description = "The Domain Name of the Cloudfront s3 log Bucket"
  type        = string  
}
