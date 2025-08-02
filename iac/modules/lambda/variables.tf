###############################
# LAMBDA DELETE S3 IMAGES TABLE
###############################
variable "iam_role_delete_s3_lambda_arn" {
  description = "ARN of the Iam Role for the Delete s3 images Lambda"
  type        = string
}

variable "lambda_delete_s3_images_name"{
  description = "Name of the s3 delete images Lambda Function"
  type        = string  
}

variable "trigger_lambda_delete_s3_images_name"{
  description = "Name of the s3 delete images Lambda Event Bridge Trigger"
  type        = string  
}

variable "s3_image_bucket_name" {
  description = "Name of the S3 bucket where images are stored"
  type        = string
}

variable "s3_images_delete_timeout" {
  description = "Timeout in days for deleting old images from S3"
  type        = number
  default     = 30
}