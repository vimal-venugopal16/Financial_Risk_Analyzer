import boto3
from strands import Agent
from strands.tools import tool

# -------------------------------
# Tools deployed
# -------------------------------
@tool
def read_customer_creditdata(bucket: str, key: str) -> str:
    bucket = 'awsstrands-riskanalyzer'
    key = 'bank_customer_repayment_data.csv'
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8")

@tool
def read_customer_profile(table_name: str) -> dict:
    table_name = 'riskanalysis_customer_profilesV1'
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    all_items = []
    response = None

    while True:
        if not response:
            response = table.scan()
        else:
            response = table.scan(ExclusiveStartKey=response.get('LastEvaluatedKey'))

        all_items.extend(response.get('Items', []))
        if 'LastEvaluatedKey' not in response:
            break
    return all_items
