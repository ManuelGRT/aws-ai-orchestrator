variable "nlb_orchestratorAi_arn" {
  description = "ARN orchestratorAi NLB"
  type        = string
}

variable "nlb_orchestratorAi_dns_name" {
  description = "DNS name orchestratorAi NLB"
  type        = string
}

variable "public_apigw_name" {
  description = "Name of the public API Gateway"
  type        = string
}

variable "public_apigw_endpoint_type" {
  description = "Type of the public endpoint"
  type        = list(string)
}

variable "apigw_stage_name" {
  description = "Name of the API GW stage"
  type        = string
}

variable "apigw_logging_level" {
  description = "Name of the API GW logging level"
  type        = string
}

variable "public_vpc_link_name" {
  description = "Name of public VPC Link"
  type        = string
}

variable "vpces" {
  description = "vpcs ids"
  type        = list(string)
}

variable "public_cognito_user_pool_arn" {
  description = "ARN of the cognito usar pool"
  type        = string
}

variable "public_cognito_user_pool_id" {
  description = "ID of the cognito user pool"
  type        = string
}

variable "public_apigateway_custom_domain_name" {
  description = "Name of the Public Api Gateway Custom Domain Name"
  type        = string
}

variable "public_acm_certificate_arn" {
  description = "ARN of the Public ACM Certificate"
  type        = string  
}