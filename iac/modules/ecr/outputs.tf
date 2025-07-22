output "ecr_orchestratorAi_repository_url" {
  description = "The URL of the Trace AI repository"
  value       = aws_ecr_repository.orchestrator_repo.repository_url
}

output "ecr_modelAi1_repository_url" {
  description = "The URL of the modelAi1 repository"
  value       = aws_ecr_repository.modelAi1_repo.repository_url
}

output "ecr_modelAi2_repository_url" {
  description = "The URL of the modelAi2 repository"
  value       = aws_ecr_repository.modelAi2_repo.repository_url
}

output "ecr_modelAi3_repository_url" {
  description = "The URL of the Kitt AI repository"
  value       = aws_ecr_repository.modelAi3_repo.repository_url
}