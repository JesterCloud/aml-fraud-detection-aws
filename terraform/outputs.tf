# Know what has been created and ARN.

output "s3_input_bucket" {
  description = "Suben las transacciones para procesar"
  value       = aws_s3_bucket.input.bucket
}

output "s3_output_bucket" { # Guarda Lambda los resultados después del scoring
  value       = aws_s3_bucket.output.bucket
}

output "lambda_function_name" {  # Nombre de la función Lambda desplegada
  value       = aws_lambda_function.fraud_scorer.function_name
}

output "dynamodb_table_name" { # NResultados hsitoricos
  value       = aws_dynamodb_table.results.name
}

output "sns_topic_arn" {
  description = "ARN del topic SNS de alertas"
  value       = aws_sns_topic.alerts.arn
}