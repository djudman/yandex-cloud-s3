import base64
import datetime
import hashlib
import os
from http.client import HTTPConnection

from .errors import YandexCloudS3ApiError
from .signature import create_signature


'''
All object methods: https://cloud.yandex.ru/docs/storage/s3/api-ref/object
'''


def __s3_api_request(
        endpoint: str,
        http_method: str,
        payload: bytes = None,
        headers: dict = None,
        region: str = 'ru-central1',
        access_key_id: str = None,
        access_key: str = None
    ) -> bytes:

    access_key_id = access_key_id or os.getenv('YANDEX_CLOUD_S3_ACCESS_KEY_ID')
    access_key = access_key or os.getenv('YANDEX_CLOUD_S3_ACCESS_KEY')
    utc_dt = datetime.datetime.utcnow()
    short_date = utc_dt.strftime('%Y%m%d')
    date = utc_dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    service = 's3'
    signed_headers = headers or {}
    signed_headers.update({
        'Host': 'storage.yandexcloud.net',
        'Date': date,  # date format: Thu, 18 Jan 2018 09:57:35 GMT
    })
    if payload:
        content_length = len(payload)
        content_md5 = base64.b64encode(hashlib.md5(payload).digest()).decode()
        payload_hash = hashlib.sha256(payload).hexdigest()
        signed_headers.update({
            'x-amz-content-sha256': payload_hash,
            'Content-Type': 'application/octet-stream',
            'Content-Length': content_length,
            'Content-MD5': content_md5,
        })
    else:
        payload = b''
    headers_list = [(name, value) for name, value in signed_headers.items()]
    aws4_signature = create_signature(region, service, http_method, endpoint,
                                      headers_list, payload, access_key, utc_dt)
    headers_names = sorted([name.lower().strip() for name, _ in headers_list])
    signed_headers['Authorization'] = 'AWS4-HMAC-SHA256 '\
                                     f'Credential={access_key_id}/{short_date}/{region}/{service}/aws4_request, '\
                                     f'SignedHeaders={";".join(headers_names)}, '\
                                     f'Signature={aws4_signature}'
    connection = HTTPConnection('storage.yandexcloud.net')
    connection.request(http_method, endpoint, payload, signed_headers)
    response = connection.getresponse()
    response_data = response.read()
    if response.status not in (200,):
        raise YandexCloudS3ApiError(response.status, response_data)
    connection.close()
    return response_data


# upload
def upload_file(
        filepath: str,
        bucket: str,
        object_key: str,
        storage_class: str = 'COLD',
        access_key_id: str = None,
        access_key: str = None,
        region: str = 'ru-central1'
    ):
    '''
    Upload a file to yandex cloud object storage synchronously.

    Parameters:
    filepath: Path to file that you want upload to yandex cloud object storage.
    bucket: Name of bucket. Required, but None by default. If there is
            environment variable YANDEX_CLOUD_S3_BUCKET, it will be used.
    object_key: 
    '''

    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)
    # TODO: chunked upload if file is big enough (1G | 500M | 100M)
    with open(filepath, 'rb') as f:
        data = f.read()

    return upload_bytes(
        data,
        bucket,
        object_key,
        storage_class,
        region,
        access_key_id,
        access_key
    )


def upload_bytes(
        data: bytes,
        bucket: str,
        object_key: str,
        storage_class: str = 'COLD',
        region: str = 'ru-central1',
        access_key_id: str = None,
        access_key: str = None
    ):

    headers = {
        # TODO: support 'x-amz-content-sha256': 'STREAMING-AWS4-HMAC-SHA256-PAYLOAD'
        'x-amz-storage-class': storage_class,
    }
    return __s3_api_request(
        f'/{bucket}/{object_key}',
        'PUT',
        payload=data,
        headers=headers,
        region=region,
        access_key_id=access_key_id,
        access_key=access_key
    )


# get
def get_object(
        bucket: str,
        object_key: str,
        region: str = 'ru-central1',
        access_key_id: str = None,
        access_key: str = None
    ) -> bytes:

    return __s3_api_request(
            f'/{bucket}/{object_key}',
            'GET',
            region=region,
            access_key_id=access_key_id,
            access_key=access_key
        )
