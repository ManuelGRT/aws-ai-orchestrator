output "cognito_user_pool_arn" {
  description = "ARN of the Cognito User Pool"
  value       = aws_cognito_user_pool.user_pool.arn
}

output "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.user_pool.id
}

output "cognito_domain" {
  description = "Domain of the Cognito"
  value       = aws_cognito_user_pool_domain.cognito_domain.domain
}

/*
output "cognito_client_id" {
  description = "ID of the Cognito App Client"
  value       = aws_cognito_user_pool_client.app_client.id
}

output "cognito_client_secret_id" {
  description = "Secret ID of the Cognito App Client"
  value       = aws_cognito_user_pool_client.app_client.client_secret
}
*/