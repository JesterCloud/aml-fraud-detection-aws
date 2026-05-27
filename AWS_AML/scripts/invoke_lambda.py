import boto3
import json

lambda_client = boto3.client(
    'lambda',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

event = {
    'Records': [{
        's3': {
            'bucket': {'name': 'aml-fraud-transactions-input'},
            'object': {'key': 'transactions.csv'}
        }
    }]
}

response = lambda_client.invoke(
    FunctionName='aml-fraud-scorer',
    InvocationType='RequestResponse',
    Payload=json.dumps(event)
)

result = response['Payload'].read().decode()
print(result)