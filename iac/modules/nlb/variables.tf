variable "subnets" {
  description = "Subnets"
  type        = list(string)
}

variable "vpc_id" {
  description = "VPC id used in NBL"
  type        = string
}

variable "orchestrator_nlb_name" {
  description = "orchestrator ai NLB name"
  type        = string
}

variable "orchestrator_nlb_target_group" {
  description = "orchestrator ai NLB target group name"
  type        = string
}