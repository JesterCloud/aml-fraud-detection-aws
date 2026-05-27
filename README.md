# AML Fraud Detection Pipeline on AWS

A real-time AML transaction scoring engine built on AWS, designed to detect suspicious financial activity using a multi-signal risk model. Transactions are scored automatically as they arrive, and high-risk cases trigger immediate alerts.

AML domain knowledge with cloud-native architecture (AWS Running locally with LocalStack), every design decision reflects how fraud detection actually works in financial institutions.

## --- 🔐 Tech stack
- **AWS Lambda** — Python 3.11 scoring engine
- **Amazon S3** — Raw input and processed output storage
- **Amazon DynamoDB** — Decision history and audit trail
- **Amazon SNS** — Real-time alerts for high-risk transactions
- **Amazon CloudWatch** — Logging and monitoring
- **Terraform** — Full infrastructure as code
- **LocalStack** — Local AWS emulation for development
- **Prerequisites:** Docker Desktop, LocalStack Desktop, Terraform, Python 3.11, awscli-local

## --- How it works
When a transaction file lands in S3, it kicks off an automated pipeline:
1. **S3** receives the raw transaction data
2. **Lambda** scores each transaction using a weighted risk model
3. Results are stored in **DynamoDB** for historical analysis
4. High-risk transactions (score ≥ 80) trigger an **SNS** alert
5. **CloudWatch** logs every decision for audit and debugging

S3 Input → Lambda (scoring) → DynamoDB + S3 Output
↘ SNS Alert (score ≥ 80)
↘ CloudWatch (all logs)

## --- Risk scoring model
A transaction can trigger multiple signals at once but each transaction is evaluated against seven risk signals. Signals are independent

| Signal | Description | Weight |
|---|---|---|
| `geo_mismatch` | Card country doesn't match payment country | +20 |
| `ip_billing_mismatch` | IP address doesn't match billing address | +20 |
| `high_velocity` | Too many transactions in a short time window | +25 |
| `vpn_usage` | User is masking their real location | +15 |
| `chargeback_history` | Account has prior fraudulent chargebacks | +30 |
| `new_account` | Account created less than 7 days ago | +10 |
| `high_amount` | Amount is unusually high for this account profile | +15 |

## Decision thresholds
| Score | Decision | What happens |
|---|---|---|
| 0 – 29 | ✅ APPROVE | Transaction goes through normally |
| 30 – 59 | 👀 REVIEW | Flagged for manual analyst review |
| 60 – 79 | 🔐 3DS_REQUIRED | Customer challenged with strong authentication |
| 80+ | 🚨 BLOCK | Transaction blocked + SNS alert fired immediately |


## --- Project structure
aml-fraud-detection-aws/
├── terraform/
│   ├── provider.tf       (LocalStack endpoints)
│   ├── main.tf           All AWS resources
│   ├── variables.tf      
│   └── outputs.tf        Resource names printed after deploy
├── lambda/
│   └── handler.py        Scoring engine — the core logic
├── data/
│   └── transactions.csv  Dataset (20 transactions)
├── scripts/
│   └── test_pipeline.py  End-to-end test script
└── docs/
└── architecture.png      architecture diagram


## Running locally
**Prerequisites:** Docker Desktop, LocalStack Desktop, Terraform, Python 3.11, awscli-local
```bash
# 1.Deploy infrastructure
cd terraform
terraform init
terraform apply -auto-approve

# 2.Run the pipeline
cd ..
python scripts/test_pipeline.py
```

## Deploying to real AWS
```bash
terraform init
terraform apply


terraform destroy
```

Expected output:
📤 Uploading transactions.csv to S3...
✅ File uploaded successfully
📊 Results in DynamoDB:
TXN015 | Score: 115 | BLOCK        | Signals: geo_mismatch, ip_billing_mismatch, high_velocity, vpn_usage, chargeback_history, new_account, high_amount
TXN007 | Score: 105 | BLOCK        | Signals: geo_mismatch, ip_billing_mismatch, high_velocity, vpn_usage, chargeback_history, high_amount

📈 Summary:
✅ APPROVE      : 5 transactions
👀 REVIEW       : 6 transactions
🔐 3DS_REQUIRED : 4 transactions
🚨 BLOCK        : 5 transactions

## Why this project exists
Fraud detection is one of those domains where the gap between theory and practice is enormous. Most AML systems in production are black boxes — this project makes the scoring logic explicit and auditable, which is exactly what regulators expect.

The signal weights are based on real fraud typologies used in payment risk teams. The thresholds (30/60/80) reflect common industry cutoffs for review queues and 3DS authentication triggers.


## Author: **Giovanny Galindo**
[LinkedIn](https://www.linkedin.com/in/giogalindo470/) · [GitHub](https://github.com/JesterCloud)
