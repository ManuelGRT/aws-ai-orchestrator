##################################
# IAM ROLE ECS TASK EXECUTION ROLE
##################################
# ECS Task Execution Role
resource "aws_iam_role" "ecs_task_execution_role" {
  name = var.task_execution_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  lifecycle {
    ignore_changes = [
      name
    ]
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


########################
# IAM ROLE ECS TASK ROLE
########################
# ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.orchestrator_ecs_task_definition_name}-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Task Role Policy
resource "aws_iam_role_policy" "ecs_task_role_policy" {
  name = "${var.orchestrator_ecs_task_definition_name}-task-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "firehose:PutRecord",
          "firehose:PutRecordBatch"
        ],
        Resource =  "*"
      },
      {
        Effect = "Allow",
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ],
        Resource =  "*"
      }
    ]
  })
}

# Task Role s3 Inline policy
resource "aws_iam_role_policy" "ecs_task_role_s3_policy" {
  name = "s3-inline-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "S3ReadWriteAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.s3_image_bucket_arn,
          "${var.s3_image_bucket_arn}/*"
        ]
      },
      /*{
        Sid = "KMSKeyUsage"
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = var.kms_key_arn
      }*/
    ]
  })
}


#############################
# IAM ROLE API GATEWAY
#############################
resource "aws_iam_role" "apigw_logs_role" {
  name = "APIGatewayCloudWatchLogsRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "apigateway.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "apigw_logs_policy" {
  role       = aws_iam_role.apigw_logs_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

###########################
# IAM ROLE DELETE S3 IMAGES
###########################
resource "aws_iam_role" "lambda_delete_s3_iam_role" {
  name = var.lambda_delete_s3_iam_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_delete_s3_iam_role_basic_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_delete_s3_iam_role.name
}

resource "aws_iam_role_policy" "lambda_delete_s3_iam_role_policy" {
  name        = "lambda-s3-cleanup-policy"
  role        = aws_iam_role.lambda_delete_s3_iam_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:DeleteObject"
        ],
        Resource = [
          var.s3_image_bucket_arn,
          "${var.s3_image_bucket_arn}/*"
        ]
      }
    ]
  })
}

