import json
import os

def lambda_handler(event, context):
    print("Event: ", json.dumps(event, indent=2))
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Hello from Python Lambda!",
            "environment": os.environ.get('ENVIRONMENT', 'development'),
            "input": event
        })
    }