############################
# WAF ACL PUBLIC API GATEWAY
############################
resource "aws_wafv2_web_acl" "api_gateway_waf" {
  name        = var.waf_apigateway_name
  description = "WAF for Public API on API Gateway Edge Optimized"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 0

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
      }
    }

    override_action {
      none {}
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
    priority = 1

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"

        rule_action_override {
          action_to_use {
            allow {}
          }
          name = "CrossSiteScripting_BODY"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "SizeRestrictions_BODY"
        }
      } 
    }
    override_action {
      none {}
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesAnonymousIpList"
    priority = 2

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesAnonymousIpList"
        rule_action_override {
          action_to_use {
            allow {}
          }
          name = "HostingProviderIPList"
        }
      }
    }

    override_action {
      none {}
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesAnonymousIpList"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesAmazonIpReputationList"
    priority = 3

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesAmazonIpReputationList"
      }
    }

    override_action {
      none {}
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesAmazonIpReputationList"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesAdminProtectionRuleSet"
    priority = 4

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesAdminProtectionRuleSet"
      }
    }

    override_action {
      none {}
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesAdminProtectionRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesSQLiRuleSet"
    priority = 5

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesSQLiRuleSet"
      }
    }

    override_action {
      none {}
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "api_gateway-waf"
    sampled_requests_enabled   = true
  }

}

resource "aws_wafv2_web_acl_association" "waf_apigategay_association" {
  resource_arn = var.apigateway_stage_arn
  web_acl_arn  = aws_wafv2_web_acl.api_gateway_waf.arn
}

resource "aws_wafv2_web_acl_logging_configuration" "waf_apigateway_logging" {
  
  log_destination_configs = [
    var.s3_apigw_waf_bucket_arn
  ]

  resource_arn = aws_wafv2_web_acl.api_gateway_waf.arn

  logging_filter {
    default_behavior = "DROP"

    filter {
      behavior = "KEEP" 
      requirement = "MEETS_ANY" 

      condition {
        action_condition {
          action = "BLOCK"
        }
      }

      dynamic "condition" {
        for_each = [
          "awswaf:managed:aws:known-bad-inputs:JavaDeserializationRCE_URIPath",
          "awswaf:managed:aws:known-bad-inputs:Propfind_Method",
          "awswaf:managed:aws:known-bad-inputs:Log4JRCE_URIPath",
          "awswaf:managed:aws:known-bad-inputs:JavaDeserializationRCE_Body",
          "awswaf:managed:aws:known-bad-inputs:JavaDeserializationRCE_Header",
          "awswaf:managed:aws:known-bad-inputs:JavaDeserializationRCE_QueryString",
          "awswaf:managed:aws:known-bad-inputs:Log4JRCE_QueryString",
          "awswaf:managed:aws:known-bad-inputs:Log4JRCE_Body",
          "awswaf:managed:aws:known-bad-inputs:Log4JRCE_Header",
          "awswaf:managed:aws:known-bad-inputs:ExploitablePaths_URIPath",
          "awswaf:managed:aws:known-bad-inputs:Host_Localhost_Header",
          "awswaf:managed:aws:core-rule-set:SizeRestrictions_URIPath",
          "awswaf:managed:aws:core-rule-set:GenericRFI_QueryArguments",
          "awswaf:managed:aws:core-rule-set:EC2MetaDataSSRF_Body",
          "awswaf:managed:aws:core-rule-set:SizeRestrictions_QueryString",
          "awswaf:managed:aws:core-rule-set:CrossSiteScripting_Body",
          "awswaf:managed:aws:core-rule-set:SizeRestrictions_Body",
          "awswaf:managed:aws:core-rule-set:RestrictedExtensions_QueryArguments",
          "awswaf:managed:aws:core-rule-set:CrossSiteScripting_QueryArguments",
          "awswaf:managed:aws:core-rule-set:EC2MetaDataSSRF_QueryArguments",
          "awswaf:managed:aws:core-rule-set:GenericLFI_URIPath",
          "awswaf:managed:aws:core-rule-set:GenericRFI_Body",
          "awswaf:managed:aws:core-rule-set:GenericLFI_Body",
          "awswaf:managed:aws:core-rule-set:BadBots_Header",
          "awswaf:managed:aws:core-rule-set:EC2MetaDataSSRF_Cookie",
          "awswaf:managed:aws:core-rule-set:SizeRestrictions_Cookie_Header",
          "awswaf:managed:aws:core-rule-set:NoUserAgent_Header",
          "awswaf:managed:aws:core-rule-set:EC2MetaDataSSRF_URIPath",
          "awswaf:managed:aws:core-rule-set:RestrictedExtensions_URIPath",
          "awswaf:managed:aws:core-rule-set:CrossSiteScripting_Cookie",
          "awswaf:managed:aws:core-rule-set:GenericRFI_URIPath",
          "awswaf:managed:aws:core-rule-set:CrossSiteScripting_URIPath",
          "awswaf:managed:aws:core-rule-set:GenericLFI_QueryArguments",
          "awswaf:managed:aws:anonymous-ip-list:AnonymousIPList",
          "awswaf:managed:aws:anonymous-ip-list:HostingProviderIPList",
          "awswaf:managed:aws:amazon-ip-list:AWSManagedIPDDoSList",
          "awswaf:managed:aws:amazon-ip-list:AWSManagedReconnaissanceList",
          "awswaf:managed:aws:amazon-ip-list:AWSManagedIPReputationList",
          "awswaf:managed:aws:admin-protection:AdminProtection_URIPath"
        ]
        content {
          label_name_condition {
            label_name = condition.value
          }
          
        }
      }
    }
  }
}