# Infrastructure (Terraform + LocalStack)

Provisions the AWS services Consentinel relies on, against
[LocalStack](https://localstack.cloud/) so it runs free and offline:

| Resource | Purpose |
| --- | --- |
| **S3 bucket** `consentinel-evidence` | Stores evidence that a compliance request was carried out (versioned, private). |
| **SQS queue** `consentinel-compliance-requests` | Hands requests to asynchronous erasure/export workers. |

## Usage

Start LocalStack (via the root `docker-compose.yml`), then:

```bash
cd infra
terraform init
terraform apply -auto-approve
terraform output
```

Inspect the created resources with the AWS CLI pointed at LocalStack:

```bash
aws --endpoint-url http://localhost:4566 s3 ls
aws --endpoint-url http://localhost:4566 sqs list-queues
```

## Targeting real AWS

The resources are plain AWS resources. To deploy to a real account, remove the
`endpoints {}` block and dummy credentials in `main.tf` and supply real
credentials via the standard AWS provider mechanisms.
