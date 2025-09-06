variable "hosted_zone_name" {
  description = "Name of the Private Hosted Zone"
  type        = string  
}

variable "vpc_id" {
  description = "VPC id used in ALB"
  type        = string
}

variable "hosted_zone_app_record_name" {
  description = "Name of the Private Hosted Zone Application Record"
  type        = string  
}

variable "hosted_zone_id" {
  description = "Id of the Private Hosted Zone"
  type        = string  
}

variable "hosted_zone_api_record_name" {
  description = "Name of the Private Hosted Zone Public Api Record"
  type        = string  
}

variable "nlb_dns_name" {
  description = "DNS name of the Network Load Balancer"
  type        = string  
}

variable "nlb_zone_id" {
  description = "Zone ID of the Network Load Balancer"
  type        = string  
}


