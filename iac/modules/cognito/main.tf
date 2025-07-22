resource "aws_cognito_user_pool" "user_pool" {
  name = var.cognito_user_pool_name

  user_pool_tier = "LITE"
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_phone_number"
      priority = 1
    }
    recovery_mechanism {
      name     = "verified_email"
      priority = 2
    }
  }
  deletion_protection = "INACTIVE"
  admin_create_user_config {
    allow_admin_create_user_only = true
  }
}

resource "aws_cognito_user_pool_domain" "cognito_domain" {
  domain       = var.cognito_user_pool_domain_name
  user_pool_id = aws_cognito_user_pool.user_pool.id
}

resource "aws_cognito_resource_server" "resource_server" {
  identifier   = "access"
  name         = "access"
  user_pool_id = aws_cognito_user_pool.user_pool.id

  scope {
    scope_name  = "fullAccess"
    scope_description = "Description of fullAccess"
  }
}

resource "aws_cognito_user_pool_client" "app_client" {
  name                         = var.cognito_user_pool_client_name

  user_pool_id                 = aws_cognito_user_pool.user_pool.id
  generate_secret              = true
  explicit_auth_flows          = ["ALLOW_REFRESH_TOKEN_AUTH"]
  enable_token_revocation      = true

  access_token_validity        = 60
  id_token_validity            = 60
  refresh_token_validity       = 30
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  allowed_oauth_flows       = ["client_credentials"]
  allowed_oauth_scopes      = ["access/fullAccess"]
  allowed_oauth_flows_user_pool_client = true
  supported_identity_providers = ["COGNITO"]
}