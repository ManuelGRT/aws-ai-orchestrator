output "public_api_stage_arn" {
  description = "The ARN of the stage of the public API Gateway"
  value       = aws_api_gateway_stage.public_stage.arn
}
