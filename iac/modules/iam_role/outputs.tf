output "task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value = aws_iam_role.ecs_task_execution_role.arn
}

output "private_ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value = aws_iam_role.ecs_task_role.arn
}

output "lambda_delete_s3_iam_role_arn" {
  description = "ARN of the IAM Role for the Lambda function that deletes S3 images"
  value = aws_iam_role.lambda_delete_s3_iam_role.arn
}