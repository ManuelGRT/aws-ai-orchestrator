variable "environment" {
  type        = string
  description = "Environment name"
}

variable "region" {
  type        = string
  description = "Region"
}

##################### API GW #####################
## PUBLIC API ##
variable "public_apigw_name" {
  type        = string
  description = "Name of the public API Gateway"
}

variable "public_apigw_endpoint_type" {
  type        = list(string)
  description = "Endpoint type for public API Gateway"
}

variable "public_apigateway_custom_domain_name" {
  description = "Name of the public apigateway Custom Domain Name"
  type        = string
}

variable "public_acm_certificate_arn" {
  description = "ARN of the Public ACM Certificate"
  type        = string
}

variable "public_acm_certificate_arn_global" {
  description = "ARN of the Global Public ACM Certificate"
  type        = string  
}

## COMMON API GW ##
variable "apigw_stage_name" {
  type        = string
  description = "API Gateway stage name"
}

variable "apigw_logging_level" {
  type        = string
  description = "API Gateway logging level"
}

##################### VPC LINK #####################
## PUBLIC VPC LINK ##
variable "public_vpc_link_name" {
  type        = string
  description = "Name of the public VPC Link"
}

##################### VPC AND SUBNETS #####################
variable "vpces" {
  type        = list(string)
  description = "List of VPC Endpoints"
}

variable "subnets" {
  type        = list(string)
  description = "List of subnet IDs"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "private_ips" {
  type        = string
  description = "Private IPS"
}

variable "vpc_s3_gateway_endpoint_id" {
  description = "Id of the s3 gateway endpoint"
  type        = string
}

variable "vpc_api_interface_endpoint_ips" {
  description = "Ips of the  api interface endpoint"
  type        = list(string)
}


##################### NLB #####################
## orchestrator ai NLB ##
variable "orchestrator_nlb_name" {
  description = "orchestrator ai NLB name"
  type        = string
}

variable "orchestrator_nlb_target_group" {
  description = "orchestrator ai NLB name"
  type        = string
}

##################### ECR #####################
variable "ecr_orchestrator_repository_name" {
  description = "ECR Trace AI repository name"
  type        = string
}

variable "ecr_modelAi1_repository_name" {
  description = "ECR modelAi1 repository name"
  type        = string
}

variable "ecr_modelAi2_repository_name" {
  description = "ECR modelAi2 repository name"
  type        = string
}

variable "ecr_modelAi3_repository_name" {
  description = "ECR modelAi3 repository name"
  type        = string
}

##################### ECS #####################
## COMMON ##
variable "ecs_cluster_name" {
  type        = string
  description = "Name of the ECS cluster"
}

variable "task_execution_role_name" {
  type        = string
  description = "Name of the ECS task execution role"
}

variable "ecs_security_group_name" {
  type        = string
  description = "Name of the ECS security group"
}

variable "kms_key_arn" {
  description = "ARN of the KMS Encryption Key"
  type        = string
}

## orchestrator ai ECS ##
variable "private_ecs_task_definition_name" {
  type        = string
  description = "Name of the private ECS task definition"
}

variable "orchestrator_ecs_task_definition_name" {
  type        = string
  description = "Name of the orchestrator ai ECS task definition"
}

variable "orchestrator_ecs_task_cpu" {
  type        = number
  description = "CPU units for orchestrator ai ECS task"
}

variable "orchestrator_ecs_task_memory" {
  type        = number
  description = "Memory for orchestrator ai ECS task in MiB"
}

variable "orchestrator_ecs_service_name" {
  type        = string
  description = "Name of the orchestrator ai ECS service"
}

## modelAi1 ECS ##

variable "modelAi1_ecs_task_definition_name" {
  type        = string
  description = "Name of the modelAi1 ECS task definition"
}

variable "modelAi1_ecs_task_cpu" {
  type        = number
  description = "CPU units for modelAi1 ECS task"
}

variable "modelAi1_ecs_task_memory" {
  type        = number
  description = "Memory for modelAi1 ECS task in MiB"
}

variable "modelAi1_ecs_service_name" {
  type        = string
  description = "Name of the modelAi1 ECS service"
}

## modelAi2 ECS ##

variable "modelAi2_ecs_task_definition_name" {
  type        = string
  description = "Name of the modelAi2 ECS task definition"
}

variable "modelAi2_ecs_task_cpu" {
  type        = number
  description = "CPU units for modelAi2 ECS task"
}

variable "modelAi2_ecs_task_memory" {
  type        = number
  description = "Memory for modelAi2 ECS task in MiB"
}

variable "modelAi2_ecs_service_name" {
  type        = string
  description = "Name of the modelAi2 ECS service"
}

## modelAi3 ECS ##

variable "modelAi3_ecs_task_definition_name" {
  type        = string
  description = "Name of the modelAi3 ECS task definition"
}

variable "modelAi3_ecs_task_cpu" {
  type        = number
  description = "CPU units for modelAi3 ECS task"
}

variable "modelAi3_ecs_task_memory" {
  type        = number
  description = "Memory for modelAi3 ECS task in MiB"
}

variable "modelAi3_ecs_service_name" {
  type        = string
  description = "Name of the modelAi3 ECS service"
}

############### WAF ACL ############################
variable "waf_apigateway_name" {
  type        = string
  description = "Name of the WAF S3 Log Bucket"
}

variable "waf_apigateway_s3_log_bucket_name" {
  type        = string
  description = "Name of the WAF S3 Log Bucket"
}

############### COGNITO ####################
variable "cognito_user_pool_name" {
  type        = string
  description = "Name of the Cognito User Pool"
}

variable "cognito_user_pool_domain_name" {
  type        = string
  description = "Name of the Domain of the Cognito User Pool"
}

variable "cognito_user_pool_client_name" {
  type        = string
  description = "Name of the Cognito User Pool App Client"
}

################## ROUTE 53 ###########################
variable "private_hosted_zone_name" {
  description = "Name of the Private Hosted Zone"
  type        = string  
}

variable "private_hosted_zone_app_record_name" {
  description = "Name of the Private Hosted Zone Application Record"
  type        = string  
}

variable "private_hosted_zone_api_record_name" {
  description = "Name of the Private Hosted Zone API Record"
  type        = string  
}

variable "private_hosted_zone_id" {
  description = "Id of the Private Hosted Zone"
  type        = string  
}

###################### S3 BUCKET ##########################
variable "image_bucket_name" {
  description = "Image bucket name"
  type        = string
}

################## SECRET MANAGER #####################
variable "secret_orchestratorAi_api_name" {
  description = "Name of the orchestratorAi Api Secret"
  type        = string
}

################# CLOUDMAP ######################
variable "cloudmap_namespace" {
  description = "Name of the Cloudmap Namespace"
  type        = string
}