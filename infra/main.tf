# Provider configured to talk to LocalStack rather than real AWS: dummy
# credentials, path-style S3, and every endpoint pointed at LocalStack. The same
# resources would provision against real AWS by dropping the endpoints block.
provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true

  endpoints {
    s3  = var.localstack_endpoint
    sqs = var.localstack_endpoint
  }
}

# Evidence store: artefacts proving a right-to-be-forgotten / access request was
# carried out (e.g. an erasure manifest), retained for audit purposes.
resource "aws_s3_bucket" "evidence" {
  bucket = var.evidence_bucket_name
}

resource "aws_s3_bucket_versioning" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket                  = aws_s3_bucket.evidence.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Request queue: lets the API hand compliance requests to asynchronous workers
# (erasure across downstream systems) without blocking the caller.
resource "aws_sqs_queue" "requests" {
  name                       = var.requests_queue_name
  message_retention_seconds  = 1209600 # 14 days
  visibility_timeout_seconds = 60
}
