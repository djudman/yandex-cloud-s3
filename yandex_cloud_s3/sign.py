import hashlib
import hmac
import os
import typing
from datetime import datetime
from urllib.parse import urlsplit, quote


def hmac_sha256(
        key: bytes,
        message: bytes,
        hex=False
    ) -> typing.Union[bytes, str]:

    obj = hmac.new(key, message, 'sha256')
    return obj.hexdigest() if hex else obj.digest()


def __create_canonical_request(
        http_method: str,
        url: str,
        headers: typing.Tuple,
        payload: bytes
    ) -> str:

    http_method = http_method.upper()
    if http_method not in ('GET', 'PUT', 'HEAD', 'DELETE'):
        raise Exception(f'Unsupported HTTP method {http_method}')
    canonical_request = [http_method]

    parsed_url = urlsplit(url)
    path = quote(parsed_url.path, safe='/~')
    canonical_request.append(path)

    canonical_query_string = ''
    if parsed_url.query:
        key_val_pairs = []
        for pair in parsed_url.query.split('&'):
            key, _, value = pair.partition('=')
            key_val_pairs.append((key, value))
        sorted_key_vals = []
        for key, value in sorted(key_val_pairs):
            sorted_key_vals.append(f'{key}={value}')
        canonical_query_string = '&'.join(sorted_key_vals)
    canonical_request.append(canonical_query_string)

    signed_headers = []
    canonical_headers = []
    for name, value in headers:
        name, value = name.lower(), str(value).strip()
        signed_headers.append(name)
        canonical_headers.append(f'{name}:{value}')
    canonical_headers = '\n'.join(sorted(canonical_headers))
    canonical_request.append(canonical_headers + '\n')

    signed_headers = ';'.join(sorted(signed_headers))
    canonical_request.append(signed_headers)

    payload_hash = hashlib.sha256(payload).hexdigest()
    canonical_request.append(payload_hash)

    return '\n'.join(canonical_request)


def __datetime_iso8601(dt: datetime):
    return dt.strftime('%Y%m%dT%H%M%SZ')


def __create_string_to_sign(
        region: str,
        service: str,
        canonical_request: str,
        utc_dt: datetime
    ) -> str:

    ts_iso8601 = __datetime_iso8601(utc_dt)
    short_date = utc_dt.strftime('%Y%m%d')
    request_hash = hashlib.sha256(canonical_request.encode()).hexdigest()
    return '\n'.join((
        'AWS4-HMAC-SHA256',
        f'{ts_iso8601}',
        f'{short_date}/{region}/{service}/aws4_request',
        f'{request_hash}'
    ))


def create_signature(
        region: str,
        service: str,
        http_method: str,
        url: str,
        headers: typing.Tuple,
        payload: bytes,
        secret_static_key: str = None,
        utc_dt: datetime = None
    ) -> bytes:

    if secret_static_key is None:
        secret_static_key = os.getenv('YANDEX_CLOUD_STATIC_KEY')
    current_date = utc_dt.strftime('%Y%m%d')

    date_key = hmac_sha256(f'AWS4{secret_static_key}'.encode(), current_date.encode())
    region_key = hmac_sha256(date_key, region.encode())
    service_key = hmac_sha256(region_key, service.encode())
    signing_key = hmac_sha256(service_key, b'aws4_request')
    canonical_request = __create_canonical_request(http_method, url, headers, payload)
    string_to_sign = __create_string_to_sign(region, service, canonical_request, utc_dt)
    return hmac_sha256(signing_key, string_to_sign.encode(), hex=True)
