import boto3

logs = boto3.client(
    'logs',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

# Ver los grupos de logs disponibles
groups = logs.describe_log_groups()
for g in groups['logGroups']:
    print(g['logGroupName'])

# Ver los logs de Lambda
try:
    streams = logs.describe_log_streams(
        logGroupName='/aws/lambda/aml-fraud-scorer',
        orderBy='LastEventTime',
        descending=True
    )
    stream_name = streams['logStreams'][0]['logStreamName']
    events = logs.get_log_events(
        logGroupName='/aws/lambda/aml-fraud-scorer',
        logStreamName=stream_name
    )
    for e in events['events']:
        print(e['message'])
except Exception as e:
    print(f"Error: {e}")