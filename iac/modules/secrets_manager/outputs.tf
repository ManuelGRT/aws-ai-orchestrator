output "orchestratorAi_api_secret_arn" {
  description = "ARN of the orchestratorAi Api Secret"
  value       = aws_secretsmanager_secret.orchestratorAi_api_secret.arn
}