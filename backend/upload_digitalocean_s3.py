import boto3

s3 = boto3.client('s3',
    region_name='us-east-1',
    endpoint_url='https://sfo3.digitaloceanspaces.com',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY'
)
