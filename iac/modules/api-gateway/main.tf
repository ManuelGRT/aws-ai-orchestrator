#### API GATEWAY ####

resource "aws_api_gateway_rest_api" "public_api" {
  name        = var.public_apigw_name
  endpoint_configuration {
    types = var.public_apigw_endpoint_type 
  }
  binary_media_types = ["multipart/form-data"]
}

#### PROXY ####
resource "aws_api_gateway_resource" "public_proxy_resource" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  parent_id   = aws_api_gateway_rest_api.public_api.root_resource_id
  path_part   = "{proxy+}"
}

# COGNITO PUBLIC API GATEWAY
resource "aws_api_gateway_authorizer" "cognito_authorizer" {
  name          = "cognitoAuthorizer"

  rest_api_id            = aws_api_gateway_rest_api.public_api.id
  type                   = "COGNITO_USER_POOLS"
  provider_arns          = [var.public_cognito_user_pool_arn]
  identity_source        = "method.request.header.Authorization"
}

resource "aws_api_gateway_method" "public_proxy_method" {
  rest_api_id   = aws_api_gateway_rest_api.public_api.id
  resource_id   = aws_api_gateway_resource.public_proxy_resource.id
  http_method   = "ANY"

  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.cognito_authorizer.id

  request_parameters = {
    "method.request.path.proxy" = true
    "method.request.header.host" = true
  }
}

#### STATUS ####
resource "aws_api_gateway_resource" "public_status_resource" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  parent_id   = aws_api_gateway_rest_api.public_api.root_resource_id
  path_part   = "status"
}

resource "aws_api_gateway_method" "status_method" {
  rest_api_id   = aws_api_gateway_rest_api.public_api.id
  resource_id   = aws_api_gateway_resource.public_status_resource.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.header.host" = true
  }
}

#### AUTHORIZE ####
resource "aws_api_gateway_resource" "public_authorize_resource" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  parent_id   = aws_api_gateway_rest_api.public_api.root_resource_id
  path_part   = "authorize"
}

resource "aws_api_gateway_method" "authorize_method" {
  rest_api_id   = aws_api_gateway_rest_api.public_api.id
  resource_id   = aws_api_gateway_resource.public_authorize_resource.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.header.host" = true
  }
}

#### VPC LINK ####
resource "aws_api_gateway_vpc_link" "public_vpc_link" {
  name        = var.public_vpc_link_name
  target_arns = ["${var.nlb_orchestratorAi_arn}"]
}

resource "aws_api_gateway_integration" "public_proxy_vpc_link_integration" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_proxy_resource.id
  http_method = aws_api_gateway_method.public_proxy_method.http_method

  type                    = "HTTP_PROXY"
  integration_http_method = "ANY"
  connection_type        = "VPC_LINK"
  connection_id          = aws_api_gateway_vpc_link.public_vpc_link.id
  uri                    = "http://${var.nlb_orchestratorAi_dns_name}:80/{proxy}"

  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
    "integration.request.header.host" = "method.request.header.host"
  }
}


resource "aws_api_gateway_integration" "public_status_vpc_link_integration" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_status_resource.id
  http_method = aws_api_gateway_method.status_method.http_method

  type                    = "HTTP_PROXY"
  integration_http_method = "GET"
  connection_type        = "VPC_LINK"
  connection_id          = aws_api_gateway_vpc_link.public_vpc_link.id
  uri                    = "http://${var.nlb_orchestratorAi_dns_name}:80/status"

  request_parameters = {
    "integration.request.header.host" = "method.request.header.host"
  }
}

resource "aws_api_gateway_integration" "public_authorize_vpc_link_integration" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_authorize_resource.id
  http_method = aws_api_gateway_method.authorize_method.http_method

  type                    = "HTTP_PROXY"
  integration_http_method = "GET"
  connection_type        = "VPC_LINK"
  connection_id          = aws_api_gateway_vpc_link.public_vpc_link.id
  uri                    = "http://${var.nlb_orchestratorAi_dns_name}:80/authorize"

  request_parameters = {
    "integration.request.header.host" = "method.request.header.host"
  }
}

resource "aws_api_gateway_method" "public_options_method" {
  rest_api_id   = aws_api_gateway_rest_api.public_api.id
  resource_id   = aws_api_gateway_resource.public_proxy_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "public_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_proxy_resource.id
  http_method = aws_api_gateway_method.public_options_method.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "public_options_200" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_proxy_resource.id
  http_method = aws_api_gateway_method.public_options_method.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "public_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  resource_id = aws_api_gateway_resource.public_proxy_resource.id
  http_method = aws_api_gateway_method.public_options_method.http_method
  status_code = aws_api_gateway_method_response.public_options_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT,DELETE'",
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

resource "aws_api_gateway_deployment" "public_deployment" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  
  depends_on = [
    aws_api_gateway_integration.public_proxy_vpc_link_integration
  ]

  lifecycle {
    create_before_destroy = true
  }

  triggers = {
    always_run = timestamp()
    #redeployment = sha1(jsonencode(aws_api_gateway_rest_api.public_api.body))
  }
}

resource "aws_api_gateway_stage" "public_stage" {
  deployment_id = aws_api_gateway_deployment.public_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.public_api.id
  stage_name    = var.apigw_stage_name

  variables = {
    cognitoUserPoolID = var.public_cognito_user_pool_id
  }
}

resource "aws_api_gateway_method_settings" "public_all" {
  rest_api_id = aws_api_gateway_rest_api.public_api.id
  stage_name  = aws_api_gateway_stage.public_stage.stage_name
  method_path = "*/*" 

  settings {
    throttling_burst_limit = 1000
    throttling_rate_limit  = 100
    metrics_enabled = true
    logging_level   = var.apigw_logging_level
  }
}

/*
resource "aws_api_gateway_domain_name" "public_custom_domain_name" {
  domain_name = var.public_apigateway_custom_domain_name

  certificate_arn = var.public_acm_certificate_arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  security_policy = "TLS_1_2"
}

resource "aws_api_gateway_base_path_mapping" "public_api_mapping" {
  domain_name = aws_api_gateway_domain_name.public_custom_domain_name.domain_name
  api_id = aws_api_gateway_rest_api.public_api.id
  stage_name  = var.apigw_stage_name
}
*/