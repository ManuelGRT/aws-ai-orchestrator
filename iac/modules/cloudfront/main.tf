### MODULO CLOUDFRONT ###
resource "aws_cloudfront_origin_access_identity" "s3_oai" {
  comment = "Setup access from CloudFront to the orchestrator-ai-public-app bucket ( read )"
}

data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

resource "aws_cloudfront_response_headers_policy" "remove_server_header" {
  name = "remove_server_headers_policy"

  remove_headers_config {
    items {
      header = "Server"
    }
    
    items {
      header = "x-amzn-remapped-server"
    }
  }
}

resource "aws_cloudfront_distribution" "cloudfront" {
  enabled             = true
  staging             = false
  is_ipv6_enabled     = true

  default_root_object = "index.html"
  price_class         = "PriceClass_100"
  http_version        = "http2and3"
  retain_on_delete    = false
  wait_for_deployment = false

  # web_acl_id          = var.waf_acl_arn
  # aliases             = [var.public_alternate_domain_name]

  origin {
    domain_name = var.s3_public_app_bucket_regional_domain_name
    origin_id   = "s3_one"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.s3_oai.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    target_origin_id       = "s3_one"
    viewer_protocol_policy = "allow-all"
    compress               = true
    allowed_methods        = ["GET", "HEAD"]

    cached_methods         = ["GET", "HEAD"]

    cache_policy_id = data.aws_cloudfront_cache_policy.caching_optimized.id
    
    response_headers_policy_id = aws_cloudfront_response_headers_policy.remove_server_header.id
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  /*
  logging_config {
    include_cookies = false
    bucket          = var.s3_cloudfront_log_bucket_domain_name
    prefix          = "cloudfront"
  }
  */

  viewer_certificate {
    # acm_certificate_arn            = var.public_acm_certificate_arn
    cloudfront_default_certificate = true
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = "sni-only"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}