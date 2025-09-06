#### ORCHESTRATOR AI API NLB ####

resource "aws_lb" "orchestratorAi_nbl" {
  name               = var.orchestrator_nlb_name
  internal          = true
  load_balancer_type = "network"
  subnets           = var.subnets
  enable_deletion_protection = false

  lifecycle {
    ignore_changes = [
      name
    ]
  }
}

resource "aws_lb_listener" "orchestratorAi_nlb_listener_80" {
  load_balancer_arn = aws_lb.orchestratorAi_nbl.arn
  port              = "80"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.orchestratorAi_target_group.arn
  }
}

resource "aws_lb_target_group" "orchestratorAi_target_group" {
  name        = var.orchestrator_nlb_target_group
  port        = 80
  protocol    = "TCP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    protocol            = "TCP"
    port               = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 2
    interval           = 10
  }
}