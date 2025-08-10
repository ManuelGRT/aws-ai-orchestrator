# PROJECT VAARIABLES
region = "eu-west-1"

### API GW ###
public_apigw_name = "public-api-gateway"
public_apigw_endpoint_type = ["REGIONAL"]
## COMMON ##
apigw_stage_name = "v1"
apigw_logging_level = "INFO"

### VPC LINK ###
public_vpc_link_name = "public-apigw-nlb-vpclink"

### VPC AND SUBNETS ###
subnets = ["subnet-03a620f359a2fbf51", "subnet-05a7bb25a8774fbf0", "subnet-088d1aba7296e461a"]
vpc_id = "vpc-002580fbabfc2c5fa"
vpc_s3_gateway_endpoint_id = ""
public_acm_certificate_arn= ""
public_apigateway_custom_domain_name= ""

### NLB ###
## OCHESTRATOR AI NLB ##
orchestrator_nlb_name = "nlb-orchestrator-ai"
orchestrator_nlb_target_group = "nlb-orchestrator-ai-tg"

### ECR ###
ecr_orchestrator_repository_name = "orchestrator-ai-api-repository"
ecr_modelAi1_repository_name = "model1-ai-api-repository"
ecr_modelAi2_repository_name = "model2-ai-api-repository"
ecr_modelAi3_repository_name = "model3-ai-api-repository"

### ECS ###
## COMMON ##
cloudmap_namespace = "orchestrator-ai"
ecs_cluster_name = "infra-backend-services"
task_execution_role_name = "orchestrator-ai-task-execution-role"
ecs_security_group_name = "orchestrator-ai-tasks-sg"
kms_key_arn = ""

## ORCHESTRATOR AI ECS ##
orchestrator_ai_ecs_task_definition_name = "task-orchestrator-ai-api"
orchestrator_ecs_task_cpu = 256
orchestrator_ecs_task_memory = 1024
orchestrator_ecs_service_name = "orchestrator-ai-api"

## MODEL AI 1 ECS ##
modelAi1_ecs_task_definition_name = "task-model1-ai-api"
modelAi1_ecs_task_cpu = 256
modelAi1_ecs_task_memory = 1024
modelAi1_ecs_service_name = "model1-ai-api"

## MODEL AI 2 ECS ##
modelAi2_ecs_task_definition_name = "task-model2-ai-api"
modelAi2_ecs_task_cpu = 256
modelAi2_ecs_task_memory = 1024
modelAi2_ecs_service_name = "model2-ai-api"

## MODEL AI 3 ECS ##
modelAi3_ecs_task_definition_name = "task-model3-ai-api"
modelAi3_ecs_task_cpu = 256
modelAi3_ecs_task_memory = 1024
modelAi3_ecs_service_name = "model3-ai-api"

### WAF ACL ###
waf_apigw_name = "waf-public-apigw"
waf_apigw_s3_log_bucket_name = "aws-waf-logs-public-apigw"
waf_cloudfront_name = "waf-cloudfront"
s3_cloudfront_waf_log_bucket_name = "aws-waf-logs-global-cf"

### COGNITO ###
cognito_user_pool_name = "cognito-public-auth"
cognito_user_pool_domain_name = "cg-orchestrator-ai"
cognito_user_pool_client_name = "cg-orchestrator-ai-api"

### ROUTE 53 ###
private_hosted_zone_name = ""
private_hosted_zone_app_record_name = ""
private_hosted_zone_api_record_name = ""
private_hosted_zone_id = ""

### S3 BUCKET ###
image_bucket_name = "orchestrator-ai-images"
s3_cloudfront_bucket_name = "orchestrator-ai-app"
s3_cloudfront_log_bucket_name = "orchestrator-ai-app-logs"

### SECRET MANAGER ###
secret_orchestratorAi_api_name = "orchestrator-ai-api-env"

### DYNAMODB ###
dynamo_table_name = "orchestrator-ai-api-info"
dynamo_hash_key = "request_id"
dynamo_hash_key_type = "S"

### LAMBDA ###
lambda_delete_s3_images_name = "lambda-delete-s3-images"
trigger_lambda_delete_s3_images_name = "trigger-lambda-delete-s3-images"
s3_images_delete_timeout = 30
lambda_delete_s3_iam_role_name = "lambda-delete-s3-images-role"