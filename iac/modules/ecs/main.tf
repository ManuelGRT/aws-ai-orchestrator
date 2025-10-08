#### CLOUDMAP NAMESPACE ####
resource "aws_service_discovery_http_namespace" "namespace" {
  name        = var.cloudmap_namespace
}

#### ECS ####
# ECS Service
resource "aws_ecs_cluster" "cluster" {
  name = var.ecs_cluster_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks_sg" {
  name        = var.ecs_security_group_name
  description = "Allow inbound traffic for ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["172.31.16.0/20"] # TODO: CAMBIAR
    description = "Allow from NLBs"
  }

  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    self        = true
    description = "Intracluster connectivity ICMP"
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
    description = "Intracluster connectivity TCP"
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "udp"
    self        = true
    description = "Intracluster connectivity UDP"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    ipv6_cidr_blocks = ["::/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

#### ORCHESTRATOR AI ECS ####

# ECS Task Definition
resource "aws_ecs_task_definition" "orchestratorAi_ecs_task_definition" {
  family                   = var.orchestrator_ecs_task_definition_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = var.orchestrator_ecs_task_cpu
  memory                  = var.orchestrator_ecs_task_memory
  execution_role_arn      = var.task_execution_role_arn
  task_role_arn           = var.private_ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = var.orchestrator_ecs_task_definition_name
      image     = "${var.orchestrator_container_image_url}:latest"
      essential = true
      
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          name          = "http"
          protocol      = "tcp"
          appProtocol  = "http"
        }
      ]

      environment = [
        {
          name  = "ENV_SECRET_ARN"
          value = var.orchestratorAi_api_secret_arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.orchestrator_ecs_task_definition_name}"
          "awslogs-region"        = "eu-west-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "orchestrator_api_logs" {
  name              = "/ecs/${var.orchestrator_ecs_task_definition_name}"
  retention_in_days = 30
}

# ECS Service
resource "aws_ecs_service" "orchestrator_api_ecs_service" {
  name            = var.orchestrator_ecs_service_name
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.orchestratorAi_ecs_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnets
    assign_public_ip = true 
    security_groups = [aws_security_group.ecs_tasks_sg.id]
  }

  load_balancer {
    target_group_arn = "${var.nlb_orchestrator_target_group_arn}"
    container_name   = var.orchestrator_ecs_task_definition_name
    container_port   = 80
  }

  service_connect_configuration {
    enabled = true
    namespace = aws_service_discovery_http_namespace.namespace.name

    service {
      port_name = "http"
      discovery_name = "orchestratorai-api"
      client_alias {
        port     = 80
        dns_name = "orchestratorai-api"
      }
    }
  }
}

#### MODEL AI 1 ECS ####

# ECS Task Definition
resource "aws_ecs_task_definition" "modelAi1_ecs_task_definition" {
  family                   = var.modelAi1_ecs_task_definition_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = var.modelAi1_ecs_task_cpu
  memory                  = var.modelAi1_ecs_task_memory
  execution_role_arn      = var.task_execution_role_arn
  task_role_arn           = var.private_ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = var.modelAi1_ecs_task_definition_name
      image     = "${var.modelAi1_container_image_url}:latest"
      essential = true
      
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          name          = "http"
          protocol      = "tcp"
          appProtocol  = "http"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.modelAi1_ecs_task_definition_name}"
          "awslogs-region"        = "eu-west-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "modelAi1_api_logs" {
  name              = "/ecs/${var.modelAi1_ecs_task_definition_name}"
  retention_in_days = 30
}

# ECS Service
resource "aws_ecs_service" "modelAi1_api_ecs_service" {
  name            = var.modelAi1_ecs_service_name
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.modelAi1_ecs_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnets
    assign_public_ip = true 
    security_groups = [aws_security_group.ecs_tasks_sg.id]
  }

  service_connect_configuration {
    enabled = true
    namespace = aws_service_discovery_http_namespace.namespace.name

    service {
      port_name = "http"
      discovery_name = "upscaling-ai-api"
      client_alias {
        port     = 80
        dns_name = "upscaling-ai-api"
      }
    }
  }
}

#### MODEL AI 2 ECS ####

# ECS Task Definition
resource "aws_ecs_task_definition" "modelAi2_ecs_task_definition" {
  family                   = var.modelAi2_ecs_task_definition_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = var.modelAi2_ecs_task_cpu
  memory                  = var.modelAi2_ecs_task_memory
  execution_role_arn      = var.task_execution_role_arn
  task_role_arn           = var.private_ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = var.modelAi2_ecs_task_definition_name
      image     = "${var.modelAi2_container_image_url}:latest"
      essential = true
      
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          name          = "http"
          protocol      = "tcp"
          appProtocol  = "http"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.modelAi2_ecs_task_definition_name}"
          "awslogs-region"        = "eu-west-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "modelAi2_api_logs" {
  name              = "/ecs/${var.modelAi2_ecs_task_definition_name}"
  retention_in_days = 30
}

# ECS Service
resource "aws_ecs_service" "modelAi2_api_ecs_service" {
  name            = var.modelAi2_ecs_service_name
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.modelAi2_ecs_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnets
    assign_public_ip = true 
    security_groups = [aws_security_group.ecs_tasks_sg.id]
  }

  service_connect_configuration {
    enabled = true
    namespace = aws_service_discovery_http_namespace.namespace.name

    service {
      port_name = "http"
      discovery_name = "denoising-ai-api"
      client_alias {
        port     = 80
        dns_name = "denoising-ai-api"
      }
    }
  }
}

#### MODEL AI 3 ECS ####

# ECS Task Definition
resource "aws_ecs_task_definition" "modelAi3_ecs_task_definition" {
  family                   = var.modelAi3_ecs_task_definition_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = var.modelAi3_ecs_task_cpu
  memory                  = var.modelAi3_ecs_task_memory
  execution_role_arn      = var.task_execution_role_arn
  task_role_arn           = var.private_ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = var.modelAi3_ecs_task_definition_name
      image     = "${var.modelAi3_container_image_url}:latest"
      essential = true
      
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          name          = "http"
          protocol      = "tcp"
          appProtocol  = "http"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.modelAi3_ecs_task_definition_name}"
          "awslogs-region"        = "eu-west-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "modelAi3_api_logs" {
  name              = "/ecs/${var.modelAi3_ecs_task_definition_name}"
  retention_in_days = 30
}

# ECS Service
resource "aws_ecs_service" "modelAi3_api_ecs_service" {
  name            = var.modelAi3_ecs_service_name
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.modelAi3_ecs_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnets
    assign_public_ip = true 
    security_groups = [aws_security_group.ecs_tasks_sg.id]
  }

  service_connect_configuration {
    enabled = true
    namespace = aws_service_discovery_http_namespace.namespace.name

    service {
      port_name = "http"
      discovery_name = "inpainting-ai-api"
      client_alias {
        port     = 80
        dns_name = "inpainting-ai-api"
      }
    }
  }
}