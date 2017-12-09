from zipfile import ZipFile
from io import BytesIO
import os
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.joinpath('vendored').resolve()))

from vendored import maya


class FileProcessor(object):
    def __init__(self, event, context, s3):
        self.event = event
        self.context = context
        self.s3 = s3
        self.bucket_processed = os.getenv('BUCKET_PROCESSED')

    def _s3_prefix(self):
        now = maya.now()
        now_datetime = now.datetime(to_timezone=now.local_timezone)

        return now_datetime.strftime('%Y/%m/%d')

    def _bucket_key_list(self):
        bucket_key_dict = {}

        for record in self.event.get('Records'):
            zip_file = record['s3']['object']['key']
            bucket_origin = record['s3']['bucket']['name']
            bucket_key_dict.update({'bucket': bucket_origin, 'key': zip_file})

        return [bucket_key_dict]

    def _zip_bytes_io(self, bucket, key):
        bytes_io = BytesIO()
        self.s3.download_fileobj(bucket, key, bytes_io)

        return bytes_io

    def _upload_file_obj(self, zip_bytes_io):
        with ZipFile(zip_bytes_io) as zip_obj:
            for obj_name in zip_obj.namelist():
                with zip_obj.open(obj_name) as file_obj:
                    key = f'{self._s3_prefix()}/{obj_name}'
                    self.s3.upload_fileobj(file_obj, self.bucket_processed, key)

    def main(self):
        for bucket_key_dict in self._bucket_key_list():
            bucket = bucket_key_dict.get('bucket')
            key = bucket_key_dict.get('key')

            zip_bytes_io = self._zip_bytes_io(bucket, key)
            self._upload_file_obj(zip_bytes_io)
