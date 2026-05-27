import boto3

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

response = s3.get_object(Bucket='aml-fraud-transactions-input', Key='transactions.csv')
content = response['Body'].read()

# Ver los primeros 500 bytes en raw para detectar encoding
print("RAW bytes:", content[:200])
print("---")
print("DECODED:", content[:200].decode('utf-8', errors='replace'))