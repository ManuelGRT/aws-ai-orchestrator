###############################
# LAMBDA DELETE S3 IMAGES
###############################
resource "null_resource" "resource_lambda_delete_s3_images" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command = <<EOT
      New-Item -ItemType Directory -Force -Path "${path.module}/lambdas/delete_s3_images/package"
      pip install -r "${path.module}/lambdas/delete_s3_images/src/requirements.txt" -t "${path.module}/lambdas/delete_s3_images/package"
      Copy-Item -Path "${path.module}/lambdas/delete_s3_images/src/*" -Destination "${path.module}/lambdas/delete_s3_images/package/" -Recurse -Force
    EOT
  }
}

data "archive_file" "lambda_zip_delete_s3_images" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas/delete_s3_images/package"
  output_path = "${path.module}/lambdas/delete_s3_images/lambda_function.zip"
  
  depends_on = [null_resource.resource_lambda_delete_s3_images]
}

resource "aws_lambda_function" "lambda_delete_s3_images" {
  filename         = data.archive_file.lambda_zip_delete_s3_images.output_path
  source_code_hash = data.archive_file.lambda_zip_delete_s3_images.output_base64sha256
  function_name    = var.lambda_delete_s3_images_name 
  role            = var.iam_role_delete_s3_lambda_arn
  handler         = "handler.main"
  runtime         = "python3.11"

  environment {
    variables = {
      BUCKET_NAME = var.s3_image_bucket_name
      PREFIX       = "images/"
      TIMEOUT    = var.s3_images_delete_timeout
    }

  }

  timeout     = 60
  memory_size = 128
}


resource "aws_cloudwatch_event_rule" "trigger_lambda_delete_s3_images" {
  name                = var.trigger_lambda_delete_s3_images_name
  description         = "EventBridge rule to trigger Lambda to delete old S3 images"
  schedule_expression = "cron(0 2 * * ? *)"
}

resource "aws_cloudwatch_event_target" "target_lambda_delete_s3_images" {
  rule      = aws_cloudwatch_event_rule.trigger_lambda_delete_s3_images.name
  target_id = "infra-delete-s3-images-lambda"
  arn       = aws_lambda_function.lambda_delete_s3_images.arn
}

resource "aws_lambda_permission" "eventbridge_lambda_delete_s3_images" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_delete_s3_images.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.trigger_lambda_delete_s3_images.arn
}