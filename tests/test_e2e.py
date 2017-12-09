from io import BytesIO
import time

import pytest


@pytest.mark.usefixtures('upload_zip_obj')
def test_upload_file_obj(s3, buckets, s3_prefix):
    bytes_io = BytesIO()
    key = f'{s3_prefix}/{pytest.file_zipped}'
    bucket_processed = buckets.get('BucketProcessedName')

    time.sleep(5)

    s3.download_fileobj(bucket_processed, key, bytes_io)

    assert type(bytes_io) is BytesIO
    assert bytes_io.getvalue() == pytest.body_zipped.encode()
