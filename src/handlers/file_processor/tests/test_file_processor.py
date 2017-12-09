from io import BytesIO
from zipfile import ZipFile
import os
import re

import pytest

from file_processor import FileProcessor


def test_valid_s3_prefix():
    file_processor = FileProcessor({}, {}, {})
    actual = file_processor._s3_prefix()

    assert type(actual) is str
    assert re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', actual)


def test_valid_bucket_key_list(event):
    file_processor = FileProcessor(event, {}, {})
    actual = file_processor._bucket_key_list()

    assert type(actual) is list

    for i in range(len(event)):
        assert 'bucket' in actual[i]
        assert actual[i]['bucket'] == event['Records'][i]['s3']['bucket']['name']
        assert 'key' in actual[i]
        assert actual[i]['key'].startswith('test')
        assert actual[i]['key'].endswith('.zip')


@pytest.mark.usefixtures('make_buckets', 'upload_zip_obj')
def test_zip_bytes_io(s3):
    file_processor = FileProcessor({}, {}, s3)

    actual = file_processor._zip_bytes_io(pytest.bucket_origin, pytest.key)

    assert type(actual) is BytesIO
    with ZipFile(actual) as zip_obj:
        assert zip_obj.namelist() == [pytest.file_zipped]
        with zip_obj.open(pytest.file_zipped) as file_obj:
            assert file_obj.read() == pytest.body_zipped.encode()


@pytest.mark.usefixtures('make_buckets', 'upload_zip_obj')
def test_upload_file_obj(s3, s3_prefix):
    bytes_io = BytesIO()
    key = f'{s3_prefix}/{pytest.file_zipped}'
    os.environ['BUCKET_PROCESSED'] = pytest.bucket_processed

    file_processor = FileProcessor({}, {}, s3)
    zip_bytes_io = file_processor._zip_bytes_io(pytest.bucket_origin, pytest.key)
    file_processor._upload_file_obj(zip_bytes_io)
    s3.download_fileobj(pytest.bucket_processed, key, bytes_io)

    assert type(bytes_io) is BytesIO
    assert bytes_io.getvalue() == pytest.body_zipped.encode()
