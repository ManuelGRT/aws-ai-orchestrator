#####################
# PRIVATE HOSTED ZONE 
#####################
resource "aws_route53_zone" "hosted_zone" {
  name = var.hosted_zone_name
  vpc {
    vpc_id = var.vpc_id
  }
}

/*
resource "aws_route53_record" "app_record" {
  zone_id = var.hosted_zone_id
  name    = var.hosted_zone_app_record_name
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = false
  }
}
*/

resource "aws_route53_record" "api_record" {
  zone_id = var.hosted_zone_id
  name    = var.hosted_zone_api_record_name
  type    = "A"

  alias {
    name                   = var.nlb_dns_name
    zone_id                = var.nlb_zone_id
    evaluate_target_health = false
  }
}