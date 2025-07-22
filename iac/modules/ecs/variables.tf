## ORCHESTRATOR AI ECS ##

variable "orchestrator_container_image_url" {
  description = "The URL of the orchestrator ai ECR repository"
  type        = string
}

variable "nlb_orchestrator_target_group_arn" {
  description = "orchestrator ai ARN nlb target group"
  type        = string
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

## MODEL AI ECS ##

variable "modelAi1_container_image_url" {
  description = "The URL of the modelAi1 ECR repository"
  type        = string
}

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

## MODEL AI ECS ##

variable "modelAi2_container_image_url" {
  description = "The URL of the modelAi2 ECR repository"
  type        = string
}

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

## KITT AI ECS ##

variable "modelAi3_container_image_url" {
  description = "The URL of the modelAi3 ECR repository"
  type        = string
}

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

## COMMON ##
variable "ecs_cluster_name" {
  type        = string
  description = "Name of the ECS cluster"
}

variable "task_execution_role_arn" {
  type        = string 
  description = "ARN of the ECS task execution role"
}

variable "private_ecs_task_role_arn" {
  type        = string 
  description = "ARN of the ECS task role"
}

variable "ecs_security_group_name" {
  type        = string
  description = "Name of the ECS security group"
}

variable "subnets" {
  type        = list(string)
  description = "List of subnet IDs"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "cloudmap_namespace" {
  description = "Name of the Namespace"
  type        = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS Encryption Key"
  type        = string
}

variable "private_ips" {
  type        = string
  description = "Private IPS"
}

### SECRET MANAGER ###
variable "public_api_secret_arn" {
  description = "ARN of the Public Api Secret"
  type        = string
}

variable "orchestratorAi_api_secret_arn" {
  description = "ARN of the orchestratorAi Api Secret"
  type        = string
}