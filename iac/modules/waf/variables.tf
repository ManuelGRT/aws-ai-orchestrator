#####################
# WAF ACL API GATEWAY
#####################
variable "waf_apigateway_name" {
  description = "Name of the Public Api Gateway WAF ACL"
  type        = string
}

variable "apigateway_stage_arn" {
  description = "ARN of the Public Api Gateway Stage"
  type        = string
}

variable "s3_apigw_waf_bucket_arn" {
  description = "The ARN of the Api Gateway WAF s3 Bucket"
  type        = string
}