output "evidence_bucket" {
  description = "Name of the S3 evidence bucket."
  value       = aws_s3_bucket.evidence.bucket
}

output "requests_queue_url" {
  description = "URL of the SQS compliance-requests queue."
  value       = aws_sqs_queue.requests.id
}
