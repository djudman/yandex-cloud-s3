# yandex-cloud-s3
Software development kit for object storage in Yandex Cloud

## Документация
* https://cloud.yandex.ru/docs/storage/s3/


### Общий вид запроса к API
```
{GET|HEAD|PUT|DELETE} /<bucket>/<key> HTTP/2
Host: storage.yandexcloud.net
Content-Length: length
Date: date
Authorization: authorization string (AWS Signature Version 4)

Request_body
```

Имя бакета можно указать как часть имени хоста. В этом случае запрос примет вид:
```
{GET|HEAD|PUT|DELETE} /<key>} HTTP/2
Host: <bucket>.storage.yandexcloud.net
...
```

### Идентификаторы классов хранилища
https://cloud.yandex.ru/docs/storage/concepts/storage-class#storage-class-identifiers


### Пример использования

```
import yandex_cloud_s3


yandex_cloud_s3.upload_bytes(b'Hello, world', 'test_bucket', 'test.txt')
data = yandex_cloud_s3.get_object('test_bucket', 'test.txt')
