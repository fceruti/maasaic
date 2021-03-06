from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import get_storage_class


class S3MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False


class CachedS3BotoStorage(S3Boto3Storage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        self.local_storage._save(name, content)
        file_obj = self.local_storage._open(name)
        super(CachedS3BotoStorage, self).save(name, file_obj)
        return name
