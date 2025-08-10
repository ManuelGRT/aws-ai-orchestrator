data "aws_canonical_user_id" "current" {}
# data "aws_cloudfront_log_delivery_canonical_user_id" "cloudfront" {}

##################
# S3 IMAGES BUCKET
##################
resource "aws_s3_bucket" "images_bucket" {
  bucket = var.s3_image_bucket_name
}

resource "aws_s3_bucket_versioning" "images_bucket_versioning" {
  bucket = aws_s3_bucket.images_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "images_bucket_block_public_access" {
  bucket = aws_s3_bucket.images_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "images_bucket_policy" {
  bucket = aws_s3_bucket.images_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "DenyInsecureTransport",
        Effect    = "Deny",
        Principal = {
          AWS = "*"
        },
        Action   = "s3:*",
        Resource = [
          aws_s3_bucket.images_bucket.arn,
          "${aws_s3_bucket.images_bucket.arn}/*"
        ],
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
          /*StringNotEquals = {
            "aws:SourceVpce": var.vpc_s3_gateway_endpoint_id
          }*/
        }
      }
    ]
  })
}

/*
resource "aws_s3_bucket_server_side_encryption_configuration" "images_bucket_encryption" {
  bucket = aws_s3_bucket.images_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.kms_key_arn
      sse_algorithm     = "aws:kms"
    }

    bucket_key_enabled = false
  }
}
*/

resource "aws_s3_bucket_lifecycle_configuration" "images_bucket_lifecycle" {
  bucket = aws_s3_bucket.images_bucket.id

  rule {
    id     = "S3BucketLifecycleRule"
    status = "Enabled"

    expiration {
      days = 90
    }

    noncurrent_version_expiration {
      noncurrent_days = 90 # TODO: REVISAR TIEMPO DE EXPIRACION
    }
  }
}


###################################
# S3 API GATEWAY WAF-ACL LOG BUCKET
###################################
resource "aws_s3_bucket" "waf_apigateway_s3_log_bucket" {
  bucket = var.s3_apigw_waf_log_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "waf_apigateway_s3_log_bucket" {
  bucket = aws_s3_bucket.waf_apigateway_s3_log_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_policy" "waf_apigateway_logs_policy" {
  bucket = aws_s3_bucket.waf_apigateway_s3_log_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "AWSLogDeliveryWrite20150319"
    Statement = [
      {
        Sid    = "AWSLogDeliveryWrite"
        Effect = "Allow"
        Principal = {
          Service = "delivery.logs.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.waf_apigateway_s3_log_bucket.arn}/AWSLogs/${data.aws_canonical_user_id.current.id}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl"      = "bucket-owner-full-control"
            "aws:SourceAccount" = data.aws_canonical_user_id.current.id
          }
          ArnLike = {
            "aws:SourceArn" = "arn:aws:logs:eu-west-1:${data.aws_canonical_user_id.current.id}:*"
          }
        }
      },
      {
        Sid    = "AWSLogDeliveryAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "delivery.logs.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.waf_apigateway_s3_log_bucket.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_canonical_user_id.current.id
          }
          ArnLike = {
            "aws:SourceArn" = "arn:aws:logs:eu-west-1:${data.aws_canonical_user_id.current.id}:*"
          }
        }
      }
    ]
  })
}

resource "aws_s3_bucket_public_access_block" "waf_apigw_s3_block_public_access" {
  bucket                  = aws_s3_bucket.waf_apigateway_s3_log_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


######################
# S3 PUBLIC APP BUCKET
######################
resource "aws_s3_bucket" "s3_bucket_cloudfront" {
  bucket = var.s3_cloudfront_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "s3_bucket_cloudfront_versioning" {
  bucket = aws_s3_bucket.s3_bucket_cloudfront.id
  versioning_configuration {
    status = "Enabled"
  }
}

/*
resource "aws_s3_bucket_logging" "s3_bucket_cloudfront_logging" {
  bucket = aws_s3_bucket.s3_bucket_cloudfront.id

  target_bucket = aws_s3_bucket.central_log_bucket.id
  target_prefix = var.s3_cloudfront_bucket_name
}
*/

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.s3_bucket_cloudfront.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Deny"
        Action    = ["s3:*"]
        Resource  = [
          aws_s3_bucket.s3_bucket_cloudfront.arn,
          "${aws_s3_bucket.s3_bucket_cloudfront.arn}/*"
        ]
        Principal = {
          AWS = "*"
        }
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
      {
        Effect   = "Allow"
        Action   = [
          "s3:GetBucket*",
          "s3:GetObject*",
          "s3:List*"
        ]
        Resource = [
          aws_s3_bucket.s3_bucket_cloudfront.arn,
          "${aws_s3_bucket.s3_bucket_cloudfront.arn}/*"
        ]
        Principal = {
          AWS = var.cloudfront_oai_arn
        }
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.s3_bucket_cloudfront.arn}/*"
        Principal = {
          AWS = var.cloudfront_oai_arn
        }
      }
    ]
  })
}