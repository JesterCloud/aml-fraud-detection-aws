import boto3

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

with open('data/transactions.csv', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Bytes leídos: {len(content)}")
print(f"Primera línea: {content.splitlines()[0] if content else 'VACÍO'}")

if len(content) == 0:
    print("ERROR: El archivo local está vacío")
else:
    s3.put_object(
        Bucket='aml-fraud-transactions-input',
        Key='transactions.csv',
        Body=content.encode('utf-8'),
        ContentType='text/csv'
    )
    print("CSV subido correctamente")
    
    # Verificar que quedó bien en S3
    response = s3.get_object(Bucket='aml-fraud-transactions-input', Key='transactions.csv')
    s3_content = response['Body'].read().decode('utf-8')
    print(f"Bytes en S3: {len(s3_content)}")
    print(f"Primera línea en S3: {s3_content.splitlines()[0]}")