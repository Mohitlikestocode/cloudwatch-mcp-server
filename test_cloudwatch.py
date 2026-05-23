import boto3

client = boto3.client("logs")

response = client.describe_log_streams(
    logGroupName="demo-app-logs"
)

print("Success!")
print(response)