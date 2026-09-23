"""
Lambda handler for the Tasks API.
Status: WIP — routing + create/list implemented, update/delete stubbed out.
Not yet deployed — writing this to nail down the logic before I wire up API Gateway.
"""

import json
import uuid
import os
from datetime import datetime, timezone

# import boto3  # uncomment once deploying — leaving out for now since this isn't wired to a real table yet

TABLE_NAME = os.environ.get("TASKS_TABLE", "Tasks")


def handler(event, context):
    """
    Routes based on HTTP method + resource path from API Gateway proxy integration.
    """
    method = event.get("httpMethod")
    path_params = event.get("pathParameters") or {}

    # user_id would come from the Cognito authorizer claims, not the request body/path —
    # this is important so users can't fetch/edit each other's tasks
    user_id = _get_user_id_from_claims(event)

    if method == "POST":
        return create_task(user_id, event)
    elif method == "GET" and "taskId" not in path_params:
        return list_tasks(user_id)
    elif method == "GET":
        return get_task(user_id, path_params["taskId"])
    elif method == "PUT":
        return update_task(user_id, path_params["taskId"], event)
    elif method == "DELETE":
        return delete_task(user_id, path_params["taskId"])

    return _response(400, {"error": "Unsupported method"})


def _get_user_id_from_claims(event):
    # Cognito authorizer puts verified claims here — never trust a userId from the body
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    return claims.get("sub")


def create_task(user_id, event):
    body = json.loads(event.get("body") or "{}")
    if not body.get("title"):
        return _response(400, {"error": "title is required"})

    task = {
        "userId": user_id,
        "taskId": str(uuid.uuid4()),
        "title": body["title"],
        "description": body.get("description", ""),
        "status": "PENDING",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }

    # TODO: table.put_item(Item=task) once boto3/dynamo client is wired up
    return _response(201, task)


def list_tasks(user_id):
    # TODO: table.query(KeyConditionExpression=Key("userId").eq(user_id))
    return _response(200, {"note": "not wired to DynamoDB yet", "userId": user_id})


def get_task(user_id, task_id):
    # TODO: table.get_item(Key={"userId": user_id, "taskId": task_id})
    return _response(200, {"note": "not wired to DynamoDB yet", "taskId": task_id})


def update_task(user_id, task_id, event):
    # TODO: figure out conditional update so we don't clobber concurrent edits
    return _response(501, {"error": "not implemented yet"})


def delete_task(user_id, task_id):
    # TODO: table.delete_item(...)
    return _response(501, {"error": "not implemented yet"})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
