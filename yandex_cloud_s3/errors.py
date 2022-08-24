class YandexCloudS3ApiError(Exception):
    def __init__(self, status_code: int, message: bytes):
        self.status_code = status_code
        self.message = message
        super().__init__()

    def __repr__(self) -> str:
        return f'YandexCloudS3ApiError(status_code={self.status_code}, message={self.message})'

    def __str__(self) -> str:
        return self.__repr__()

    def __unicode__(self) -> str:
        return self.__str__()
