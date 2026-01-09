import json
import os
import time
import secrets
import string
import boto3
import urllib.parse

CODE_LENGTH = 12
ALPHABET = string.ascii_letters + string.digits

s3 = boto3.client('s3')
BUCKET_NAME = os.environ["BUCKET_NAME"]
UPLOAD_EXPIRATION_SECONDS = 300  # 5 minutos
DOWNLOAD_EXPIRATION_SECONDS = 3600 # 1 hora

def _generate_code(length=CODE_LENGTH):
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))

def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*"
        },
        "body": json.dumps(body)
    }

def upload_handler(event, context):
    """
    POST /files
    Body: 
    {
        "filename": "example.txt",
        "contentType": "image/png"
    }
    """
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return _response(400, {"message": "Invalid JSON body"})

    filename = body.get("filename")
    content_type = body.get("contentType", "application/octet-stream")

    if not filename:
        return _response(400, {"message": "filename is required"})

    # Limpieza mínima del filename
    filename = filename.split("/")[-1].split("\\")[-1]

    # Object key final
    upload_code = _generate_code()
    object_key = f"{upload_code}_{filename}"

    try:
        upload_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": object_key,
                "ContentType": content_type
            },
            ExpiresIn=UPLOAD_EXPIRATION_SECONDS
        )
    except Exception as e:
        return _response(500, {"message": "Failed to generate upload URL"})

    return _response(201, {
        "objectKey": object_key,
        "uploadUrl": upload_url
    })

def download_handler(event, context):
    """
    GET /files/{objectKey}
    """
    path_params = event.get("pathParameters") or {}
    raw_key = path_params.get("objectKey")
    if not raw_key:
        return _response(400, {"message": "Missing path parameter: objectKey"})
    
    # HTTP API may pass URL-encoded path params; decode safely.
    object_key = urllib.parse.unquote(raw_key)

    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=object_key)
    except Exception as e:
        return _response(500, {"message": "Error retrieving file", "objectKey": object_key})
    
    try:
        download_url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": object_key,
            },
            ExpiresIn=DOWNLOAD_EXPIRATION_SECONDS
        )
    except Exception:
        return _response(500, {"message": "Failed to generate download URL"})
    
    # Redirect HTTP
    return {
        "statusCode": 307,
        "headers": {
            "Location": download_url,
            "Cache-Control": "no-store",
            "access-control-allow-origin": "*",
        },
        "body": ""
    }