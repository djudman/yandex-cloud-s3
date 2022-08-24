# yandex-cloud-s3
Software development kit for object storage in Yandex Cloud

## Example

```
import os
from yandex_cloud_s3 import upload_bytes, get_object


if __name__ == '__main__':
    os.environ['YANDEX_CLOUD_S3_ACCESS_KEY_ID'] = 'test'
    os.environ['YANDEX_CLOUD_S3_ACCESS_KEY'] = 'test'
    upload_bytes(b'Hello, world', 'test_bucket', 'test.txt')
    data = get_object('test_bucket', 'test.txt')
    assert data == b'Hello, world'
```

#### Links
* [Documentation](https://cloud.yandex.com/docs/storage/s3/)
* [Storage class identifiers](https://cloud.yandex.com/docs/storage/concepts/storage-class#storage-class-identifiers)
