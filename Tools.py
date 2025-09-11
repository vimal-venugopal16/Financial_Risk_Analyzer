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

@tool
def send_report(message: str) -> None:
    sns_client = boto3.client('sns', region_name='us-east-1')  # e.g., 'us-east-1'

    # Define your topic ARN and message
    topic_arn = 'arn:aws:sns:us-east-1:504711987883:RiskAnalyzer'
    subject = 'Risk Analyzer - Results'  # Optional, for email subscriptions
    phone_number='+18574926419'
    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject  # Include if you have email subscriptions
        )
        responseph = sns_client.publish(
            PhoneNumber=phone_number,
            Message=message,
            Subject=subject  # Include if you have email subscriptions
        )
    except Exception as e:
        print(f"Error publishing message: {e}")


@tool
def rules_engine(data, rules):
    violations = []
    for rule in rules:
        if eval(rule['condition']):  # e.g., data['credit_score'] < 600
            violations.append(rule['id'])
    return violations