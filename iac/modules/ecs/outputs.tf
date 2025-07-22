#### COMMON ECS ####

output "cluster_id" {
  description = "The ID of the ECS cluster"
  value       = aws_ecs_cluster.cluster.id
}

output "cluster_arn" {
  description = "The ARN of the ECS cluster"
  value       = aws_ecs_cluster.cluster.arn
}

#### PUBLIC ECS ####

output "public_service_name" {
  description = "The name of the public ECS service"
  value       = aws_ecs_service.public_api_ecs_service.name
}

output "task_definition_arn" {
  description = "The ARN of the Task Definition"
  value       = aws_ecs_task_definition.public_ecs_task_definition.arn
}

#### ORCHESTRATOR AI ECS ####

output "orchestratorAi_log_group_name" {
  description = "The name of the orchestratorAi log group"
  value       = aws_cloudwatch_log_group.orchestrator_api_logs.name
}

output "publicApi_log_group_name" {
  description = "The name of the public api log group"
  value       = aws_cloudwatch_log_group.public_api_logs.name
}