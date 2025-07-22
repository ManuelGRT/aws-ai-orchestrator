resource "aws_secretsmanager_secret" "orchestratorAi_api_secret" {
  name        = var.secret_orchestratorAi_api_name
}