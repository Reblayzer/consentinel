variable "localstack_endpoint" {
  description = "Endpoint for LocalStack's AWS-compatible API."
  type        = string
  default     = "http://localhost:4566"
}

variable "aws_region" {
  description = "AWS region (LocalStack ignores it, but the provider requires one)."
  type        = string
  default     = "eu-west-1"
}

variable "evidence_bucket_name" {
  description = "S3 bucket that stores evidence for completed compliance requests."
  type        = string
  default     = "consentinel-evidence"
}

variable "requests_queue_name" {
  description = "SQS queue that fans out compliance requests to downstream workers."
  type        = string
  default     = "consentinel-compliance-requests"
}
