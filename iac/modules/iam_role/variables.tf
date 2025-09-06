##################################
# IAM ROLE ECS TASK EXECUTION ROLE
##################################
variable "task_execution_role_name" {
  type        = string
  description = "Name of the ECS task execution role"
}

########################
# IAM ROLE ECS TASK ROLE
########################
variable "orchestrator_ecs_task_definition_name" {
  type        = string
  description = "Name of the private ECS task definition"
}

variable "kms_key_arn" {
  description = "ARN of the KMS Encryption Key"
  type        = string
}

variable "s3_image_bucket_arn" {
  description = "Image bucket name"
  type        = string
}

##################################
# IAM ROLE LAMBDA DELETE S3 IMAGES
##################################
variable "lambda_delete_s3_iam_role_name" {
  description = "Name of the IAM Role for the Lambda function that deletes S3 images"
  type        = string
}