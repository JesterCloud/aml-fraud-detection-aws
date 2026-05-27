# AWS Resources, El orden importa: 1 buckets, 2 permisos, 3 Dynamo & SNS, 4 Lambda.

# ─────────────────────────────────────────
# S3 — Los dos buckets del pipeline
# ─────────────────────────────────────────
# Bucket de entrada:
resource "aws_s3_bucket" "input" {
  bucket = var.s3_bucket_input
}

# Bucket de salida: Lambda deposita los resultados procesados
resource "aws_s3_bucket" "output" {
  bucket = var.s3_bucket_output
}

# Once something is in the bucket, esto le avisa a Lambda para que lo procese
# resource "aws_s3_bucket_notification" "trigger" {
  # bucket = aws_s3_bucket.input.id

  # lambda_function {
    # lambda_function_arn = aws_lambda_function.fraud_scorer.arn
   #  events              = ["s3:ObjectCreated:*"]  # Cualquier archivo nuevo dispara Lambda
  # }

  # depends_on = [aws_lambda_permission.allow_s3]
# }

# ─────────────────────────────────────────
# DYNAMODB — Tabla donde guardamos resultados - transaction_id es la clave primaria
# ─────────────────────────────────────────
resource "aws_dynamodb_table" "results" {
  name         = var.dynamodb_table
  billing_mode = "PAY_PER_REQUEST"  # On Demand
  hash_key     = "transaction_id"

  attribute {
    name = "transaction_id"
    type = "S"  #String
  }
}

# ─────────────────────────────────────────
# SNS
# ─────────────────────────────────────────
resource "aws_sns_topic" "alerts" {
  name = var.sns_topic_name
}

# Topic Subscription
resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ─────────────────────────────────────────
# IAM & Roles
# ─────────────────────────────────────────
resource "aws_iam_role" "lambda_role" { #Lambda Rol
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" { #Write S3, read S3, read DynamoDB, SNS and LOGS
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = ["arn:aws:s3:::${var.s3_bucket_input}/*",
                    "arn:aws:s3:::${var.s3_bucket_output}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:PutItem", "dynamodb:GetItem"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["sns:Publish"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"]
        Resource = "*"
      }
    ]
  })
}

# Permiso especial para que S3 pueda invocar Lambda (cuando llega un archivo a S3, el necesita llamar a Lambda)
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fraud_scorer.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.input.arn
}

# ─────────────────────────────────────────
# Lambda
# ─────────────────────────────────────────
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda/handler.py"
  output_path = "${path.module}/../lambda/handler.zip"
}

# Lambda function:
resource "aws_lambda_function" "fraud_scorer" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-scorer"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"  # archivo.función
  runtime          = "python3.11"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 30   # segundos máximos antes de cortar la ejecución
  memory_size      = 128  # MB — más que suficiente para este pipeline

  #Lambda variables - to avoid hard-coding 
  environment {
    variables = {
      DYNAMODB_TABLE   = var.dynamodb_table
      S3_OUTPUT_BUCKET = var.s3_bucket_output
      SNS_TOPIC_ARN    = aws_sns_topic.alerts.arn
    }
  }
}

# ─────────────────────────────────────────
# S3 Notifcation when upload info to bucket
# ─────────────────────────────────────────
resource "aws_s3_bucket_notification" "trigger" {
  bucket = aws_s3_bucket.input.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.fraud_scorer.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}