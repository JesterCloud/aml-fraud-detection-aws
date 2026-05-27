variable "aws_region" {
  default     = "us-east-1"
}

variable "project_name" { # Prefijo de los recursos creados
  default     = "aml-fraud"
}

variable "s3_bucket_input" { # Bucket_transacciones en crudo
  default     = "aml-fraud-transactions-input"
}

variable "s3_bucket_output" { # Bucket_Lambda guarda resultados
  default     = "aml-fraud-transactions-output"
}

variable "dynamodb_table" { # DynamoDB Table
  default     = "aml-fraud-results"
}

variable "sns_topic_name" { # Topic SNS dispara alertas score >= 80
  default     = "aml-fraud-alerts"
}

variable "alert_email" {
  description = "Email de alertas"
  default     = "test123@work.com" # LoclStack does show if Email was sent, but DOES NOT REALLY SEND AND EMAIL
}