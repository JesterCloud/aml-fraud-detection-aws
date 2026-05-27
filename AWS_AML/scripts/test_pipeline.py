# test_pipeline.py
# Este script simula el flujo completo del pipeline:
# sube el CSV a S3, espera a que Lambda lo procese,
# y luego consulta los resultados en DynamoDB.

import boto3
import json
import time
import os

# Apuntamos a LocalStack en lugar de AWS real
ENDPOINT = "http://localhost:4566"
REGION   = "us-east-1"

# Nombres que definimos en variables.tf
S3_INPUT  = "aml-fraud-transactions-input"
S3_OUTPUT = "aml-fraud-transactions-output"
DDB_TABLE = "aml-fraud-results"

# Clientes apuntando a LocalStack
s3       = boto3.client("s3",       endpoint_url=ENDPOINT, region_name=REGION,
                        aws_access_key_id="test", aws_secret_access_key="test")
dynamodb = boto3.resource("dynamodb", endpoint_url=ENDPOINT, region_name=REGION,
                        aws_access_key_id="test", aws_secret_access_key="test")

def upload_transactions():
    print("📤 Subiendo transactions.csv a S3...")
    csv_path = os.path.join(os.path.dirname(__file__), "../data/transactions.csv")
    s3.upload_file(csv_path, S3_INPUT, "transactions.csv")
    print("✅ Archivo subido correctamente")

def check_results():
    print("\n⏳ Esperando 3 segundos para que Lambda procese...")
    time.sleep(3)

    print("\n📊 Resultados en DynamoDB:")
    print("-" * 60)

    table   = dynamodb.Table(DDB_TABLE)
    results = table.scan()["Items"]

    # Agrupamos por decisión para ver el resumen
    summary = {"APPROVE": [], "REVIEW": [], "3DS_REQUIRED": [], "BLOCK": []}

    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        decision = r["decision"]
        summary[decision].append(r["transaction_id"])
        print(f"{r['transaction_id']} | Score: {r['score']:>3} | {decision:<12} | Señales: {', '.join(r['signals']) or 'ninguna'}")

    print("\n📈 Resumen:")
    print(f"  ✅ APPROVE      : {len(summary['APPROVE'])} transacciones")
    print(f"  👀 REVIEW       : {len(summary['REVIEW'])} transacciones")
    print(f"  🔐 3DS_REQUIRED : {len(summary['3DS_REQUIRED'])} transacciones")
    print(f"  🚨 BLOCK        : {len(summary['BLOCK'])} transacciones")

if __name__ == "__main__":
    upload_transactions()
    check_results()