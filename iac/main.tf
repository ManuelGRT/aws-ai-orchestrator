terraform {
  backend "s3" {
    encrypt                 = true
    bucket                  = "aws-ai-orchestrator-tfstate"
    key                     = "terraform.tfsate"
    region                  = "eu-west-1"
    shared_credentials_file = "~/.aws/credentials"
  }
}

provider "aws" {
  region                  = "eu-west-1"
  shared_credentials_files = ["~/.aws/credentials"]
}

module "cognito" {
  source = "./modules/cognito"

  cognito_user_pool_name = var.cognito_user_pool_name
  cognito_user_pool_domain_name = var.cognito_user_pool_domain_name
  cognito_user_pool_client_name = var.cognito_user_pool_client_name
}

module "api-gateway" {
  source = "./modules/api-gateway"

  nlb_orchestratorAi_arn = module.nlb.nlb_orchestrator_arn
  nlb_orchestratorAi_dns_name = module.nlb.nlb_orchestrator_dns_name

  public_apigw_name = var.public_apigw_name
  public_apigw_endpoint_type = var.public_apigw_endpoint_type
  public_vpc_link_name = var.public_vpc_link_name
  public_cognito_user_pool_arn = module.cognito.cognito_user_pool_arn
  public_cognito_user_pool_id = module.cognito.cognito_user_pool_id
  public_apigateway_custom_domain_name = var.public_apigateway_custom_domain_name
  public_acm_certificate_arn = var.public_acm_certificate_arn

  apigw_stage_name = var.apigw_stage_name
  apigw_logging_level = var.apigw_logging_level
}

module "nlb" {
  source = "./modules/nlb"

  orchestrator_nlb_name = var.orchestrator_nlb_name
  orchestrator_nlb_target_group = var.orchestrator_nlb_target_group

  subnets = var.subnets
  vpc_id = var.vpc_id
}

module "ecr" {
  source = "./modules/ecr"

  ecr_orchestratorAi_repository_name = var.ecr_orchestrator_repository_name
  ecr_modelAi1_repository_name = var.ecr_modelAi1_repository_name
  ecr_modelAi2_repository_name = var.ecr_modelAi2_repository_name
  ecr_modelAi3_repository_name = var.ecr_modelAi3_repository_name
}

module "ecs" {
  source = "./modules/ecs"

  orchestrator_container_image_url = module.ecr.ecr_orchestratorAi_repository_url
  modelAi1_container_image_url = module.ecr.ecr_modelAi1_repository_url
  modelAi2_container_image_url = module.ecr.ecr_modelAi2_repository_url
  modelAi3_container_image_url = module.ecr.ecr_modelAi3_repository_url

  nlb_orchestrator_target_group_arn = module.nlb.nlb_orchestrator_target_group_arn

  ecs_cluster_name = var.ecs_cluster_name
  ecs_security_group_name = var.ecs_security_group_name
  subnets = var.subnets
  vpc_id = var.vpc_id
  cloudmap_namespace = var.cloudmap_namespace
  kms_key_arn = var.kms_key_arn

  private_ecs_task_role_arn = module.iam_role.private_ecs_task_role_arn
  task_execution_role_arn = module.iam_role.task_execution_role_arn

  orchestrator_ecs_task_definition_name = var.orchestrator_ai_ecs_task_definition_name
  orchestrator_ecs_task_cpu = var.orchestrator_ecs_task_cpu
  orchestrator_ecs_task_memory = var.orchestrator_ecs_task_memory
  orchestrator_ecs_service_name = var.orchestrator_ecs_service_name

  modelAi1_ecs_task_definition_name = var.modelAi1_ecs_task_definition_name
  modelAi1_ecs_task_cpu = var.modelAi1_ecs_task_cpu
  modelAi1_ecs_task_memory = var.modelAi1_ecs_task_memory
  modelAi1_ecs_service_name = var.modelAi1_ecs_service_name

  modelAi2_ecs_task_definition_name = var.modelAi2_ecs_task_definition_name
  modelAi2_ecs_task_cpu = var.modelAi2_ecs_task_cpu
  modelAi2_ecs_task_memory = var.modelAi2_ecs_task_memory
  modelAi2_ecs_service_name = var.modelAi2_ecs_service_name

  modelAi3_ecs_task_definition_name = var.modelAi3_ecs_task_definition_name
  modelAi3_ecs_task_cpu = var.modelAi3_ecs_task_cpu
  modelAi3_ecs_task_memory = var.modelAi3_ecs_task_memory
  modelAi3_ecs_service_name = var.modelAi3_ecs_service_name

  orchestratorAi_api_secret_arn = module.secrets_manager.orchestratorAi_api_secret_arn
}

module "waf_acl" {
  source = "./modules/waf"


  # Public Api-Gateway WAF ACL
  waf_apigw_name = var.waf_apigw_name
  apigateway_stage_arn = module.api-gateway.public_api_stage_arn
  s3_apigw_waf_bucket_arn = module.s3_bucket.s3_apigw_waf_bucket_arn
}

/*
module "hosted_zone" {
  source = "./modules/route53"

  vpc_id = var.vpc_id
  hosted_zone_name = var.private_hosted_zone_name
  hosted_zone_app_record_name = var.private_hosted_zone_app_record_name
  hosted_zone_api_record_name = var.private_hosted_zone_api_record_name
  hosted_zone_id = var.private_hosted_zone_id

  nlb_dns_name = module.nlb.nlb_private_apigateway_dns_name
  nlb_zone_id = module.nlb.nlb_private_apigateway_zone_id
}
*/

module "iam_role" {
  source = "./modules/iam_role"

  kms_key_arn = var.kms_key_arn

  orchestrator_ecs_task_definition_name = var.orchestrator_ai_ecs_task_definition_name
  task_execution_role_name = var.task_execution_role_name

  s3_image_bucket_arn = module.s3_bucket.s3_images_bucket_arn
  lambda_delete_s3_iam_role_name = var.lambda_delete_s3_iam_role_name
}


module "s3_bucket" {
  source = "./modules/s3"

  s3_image_bucket_name = var.image_bucket_name
  kms_key_arn = var.kms_key_arn
  vpc_s3_gateway_endpoint_id = var.vpc_s3_gateway_endpoint_id

  s3_apigw_waf_log_bucket_name = var.waf_apigw_s3_log_bucket_name
}

module "secrets_manager" {
  source = "./modules/secrets_manager"

  secret_orchestratorAi_api_name = var.secret_orchestratorAi_api_name
}

module "lambda" {
  source = "./modules/lambda"

  iam_role_delete_s3_lambda_arn = module.iam_role.lambda_delete_s3_iam_role_arn
  lambda_delete_s3_images_name = var.lambda_delete_s3_images_name
  trigger_lambda_delete_s3_images_name = var.trigger_lambda_delete_s3_images_name
  s3_image_bucket_name = var.image_bucket_name
  s3_images_delete_timeout = var.s3_images_delete_timeout
}

module "dynamo_db" {
  source        = "./modules/dynamodb"

  table_name    = var.dynamo_table_name
  hash_key      = var.dynamo_hash_key
  hash_key_type = var.dynamo_hash_key_type
}