import json
import boto3
import os
import csv
import uuid
from datetime import datetime

DYNAMODB_TABLE   = os.environ.get("DYNAMODB_TABLE", "aml-fraud-results")
S3_OUTPUT_BUCKET = os.environ.get("S3_OUTPUT_BUCKET", "aml-fraud-transactions-output")
SNS_TOPIC_ARN    = os.environ.get("SNS_TOPIC_ARN", "")

s3       = boto3.client("s3",       endpoint_url="http://host.docker.internal:4566")
dynamodb = boto3.resource("dynamodb", endpoint_url="http://host.docker.internal:4566")
sns      = boto3.client("sns",      endpoint_url="http://host.docker.internal:4566")

def calculate_score(transaction):
    score = 0
    signals = []

    if transaction.get("geo_mismatch") == "true":
        score += 20
        signals.append("geo_mismatch")

    if transaction.get("ip_billing_mismatch") == "true":
        score += 20
        signals.append("ip_billing_mismatch")

    if transaction.get("high_velocity") == "true":
        score += 25
        signals.append("high_velocity")

    if transaction.get("vpn_usage") == "true":
        score += 15
        signals.append("vpn_usage")

    if transaction.get("chargeback_history") == "true":
        score += 30
        signals.append("chargeback_history")

    if transaction.get("new_account") == "true":
        score += 10
        signals.append("new_account")

    if transaction.get("high_amount") == "true":
        score += 15
        signals.append("high_amount")

    return score, signals


def get_decision(score):
    if score >= 80:
        return "BLOCK"
    elif score >= 60:
        return "3DS_REQUIRED"
    elif score >= 30:
        return "REVIEW"
    else:
        return "APPROVE"


def lambda_handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key    = event["Records"][0]["s3"]["object"]["key"]

    print(f"Procesando archivo: s3://{bucket}/{key}")

    response = s3.get_object(Bucket=bucket, Key=key)
    content  = response["Body"].read().decode("utf-8")
    reader   = csv.DictReader(content.splitlines())

    rows = list(reader)
    print(f"DEBUG - Filas encontradas: {len(rows)}, Headers: {reader.fieldnames}")

    results = []
    table   = dynamodb.Table(DYNAMODB_TABLE)

    for transaction in rows:
        score, signals = calculate_score(transaction)
        decision       = get_decision(score)
        transaction_id = transaction.get("transaction_id", str(uuid.uuid4()))

        result = {
            "transaction_id": transaction_id,
            "score":          score,
            "decision":       decision,
            "signals":        signals,
            "timestamp":      datetime.utcnow().isoformat(),
            "amount":         transaction.get("amount", "0"),
            "customer_id":    transaction.get("customer_id", "unknown")
        }

        table.put_item(Item=result)

        if score >= 80 and SNS_TOPIC_ARN:
            sns.publish(
                TopicArn = SNS_TOPIC_ARN,
                Subject  = f"ALERTA FRAUDE - Score {score} - {decision}",
                Message  = json.dumps(result, indent=2)
            )
            print(f"Alerta enviada para transacción {transaction_id} con score {score}")

        results.append(result)
        print(f"Transacción {transaction_id} → Score: {score} → Decisión: {decision}")

    output_key = f"results/{key.replace('.csv', '')}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
    s3.put_object(
        Bucket      = S3_OUTPUT_BUCKET,
        Key         = output_key,
        Body        = json.dumps(results, indent=2),
        ContentType = "application/json"
    )

    print(f"Resultados guardados en s3://{S3_OUTPUT_BUCKET}/{output_key}")
    return {"statusCode": 200, "body": f"Procesadas {len(results)} transacciones"}