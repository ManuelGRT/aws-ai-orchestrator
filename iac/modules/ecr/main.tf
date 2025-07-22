## ORCHESTRATOR AI API ##

resource "aws_ecr_repository" "orchestratorAi_repo" {
  name                 = var.ecr_orchestratorAi_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  lifecycle {
    ignore_changes = [
      name
    ]
  }
}

## AI MODEL 1 API ##

resource "aws_ecr_repository" "modelAi1_repo" {
  name                 = var.ecr_modelAi1_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  lifecycle {
    ignore_changes = [
      name
    ]
  }
}

## AI MODEL 2 API ##

resource "aws_ecr_repository" "modelAi2_repo" {
  name                 = var.ecr_modelAi2_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  lifecycle {
    ignore_changes = [
      name
    ]
  }
}

## AI MODEL 3 API ##

resource "aws_ecr_repository" "modelAi3_repo" {
  name                 = var.ecr_modelAi3_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  lifecycle {
    ignore_changes = [
      name
    ]
  }
}