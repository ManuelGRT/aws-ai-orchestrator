#### COMMON ECS ####

output "cluster_id" {
  description = "The ID of the ECS cluster"
  value       = aws_ecs_cluster.cluster.id
}

output "cluster_arn" {
  description = "The ARN of the ECS cluster"
  value       = aws_ecs_cluster.cluster.arn
}


#### ORCHESTRATOR AI ECS ####
output "orchestratorAi_log_group_name" {
  description = "The name of the orchestratorAi log group"
  value       = aws_cloudwatch_log_group.orchestrator_api_logs.name
}
