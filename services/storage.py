import boto3
from botocore.config import Config
import config

_client = None

def _s3():
    global _client
    if _client is None:
        _client = boto3.client(
            's3',
            endpoint_url=config.SUPABASE_S3_ENDPOINT,
            aws_access_key_id=config.SUPABASE_S3_ACCESS_KEY,
            aws_secret_access_key=config.SUPABASE_S3_SECRET_KEY,
            region_name=config.SUPABASE_S3_REGION,
            config=Config(signature_version='s3v4'),
        )
    return _client

def upload(path: str, data: bytes, content_type: str = 'application/octet-stream'):
    _s3().put_object(Bucket=config.SUPABASE_S3_BUCKET, Key=path, Body=data, ContentType=content_type)

def signed_url(path: str, expires: int = 3600) -> str:
    return _s3().generate_presigned_url(
        'get_object',
        Params={'Bucket': config.SUPABASE_S3_BUCKET, 'Key': path},
        ExpiresIn=expires,
    )

def delete(path: str):
    _s3().delete_object(Bucket=config.SUPABASE_S3_BUCKET, Key=path)
