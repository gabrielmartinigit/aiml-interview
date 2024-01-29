import os
import boto3

TABLE = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    metrics = event[1]["Metrics"]["body"]["metrics"]
    key = event[0]["Records"][0]["s3"]["object"]["key"]
    record_id = os.path.splitext(os.path.basename(key))[0]
    table = dynamodb.Table(TABLE)

    table.update_item(
        Key={"record_id": record_id},
        UpdateExpression="set report=:report, video=:video",
        ExpressionAttributeValues={
            ":report": metrics,
            ":video": key,
        },
        ReturnValues="ALL_NEW",
    )

    return {
        "statusCode": 200,
        "body": {"status": "success"},
    }
