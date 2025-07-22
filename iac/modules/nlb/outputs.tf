#### ORCHESTRATOR AI API NLB ####

output "nlb_orchestrator_arn" {
  description = "The ARN of the Application Load Balancer"
  value       = aws_lb.orchestratorAi_nbl.arn
}

output "nlb_orchestrator_dns_name" {
  description = "The DNS name of the Application Load Balancer"
  value       = aws_lb.orchestratorAi_nbl.dns_name
}

output "nlb_orchestrator_target_group_arn" {
  description = "The ARN of the Target Group"
  value       = aws_lb_target_group.orchestratorAi_target_group.arn
}

output "nlb_orchestrator_listener_arn" {
  description = "The ARN of the Listener"
  value       = aws_lb_listener.orchestratorAi_nlb_listener_80.arn
}