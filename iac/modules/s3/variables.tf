#################
# IMAGE S3 BUCKET
#################
variable "s3_image_bucket_name" {
  description = "Image bucket name"
  type        = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS Encryption Key"
  type        = string
}

variable "vpc_s3_gateway_endpoint_id" {
  description = "Id of the s3 gateway endpoint"
  type        = string
}

###############################
# API GATEWAY WAF S3 LOG BUCKET
###############################
variable "s3_apigw_waf_log_bucket_name" {
  description = "Name of the Public Api Gateway WAF ACL S3 Log Bucket"
  type        = string  
}

######################
# PUBLIC APP S3 BUCKET
######################
variable "s3_cloudfront_bucket_name" {
  description = "Name of the app S3 Bucket"
  type        = string  
}

variable "cloudfront_oai_arn" {
  description = "Cloudfront OAI Arn"
  type        = string  
}

##########################
# CLOUDFRONT S3 LOG BUCKET
##########################
variable "s3_cloudfront_log_bucket_name" {
  description = "Name of the Cloudfront S3 Log Bucket"
  type        = string  
}

##############################
# CLOUDFRONT WAF S3 LOG BUCKET
##############################
variable "s3_cloudfront_waf_log_bucket_name" {
  description = "Name of the Cloudfront WAF ACL S3 Log Bucket"
  type        = string  
}