from io import BytesIO
from zipfile import ZipFile
import json

import maya
import boto3
import pytest


@pytest.fixture(scope='session')
def s3():
    s3 = boto3.client('s3', endpoint_url='http://localhost:4572')

    return s3


@pytest.fixture(scope='session')
def s3_prefix():
    now = maya.now()
    now_datetime = now.datetime(to_timezone=now.local_timezone)
    s3_prefix = now_datetime.strftime('%Y/%m/%d')

    return s3_prefix


@pytest.fixture(scope='session')
def make_buckets(s3, request):
    pytest.bucket_origin = 'origin'
    pytest.bucket_processed = 'processed'
    buckets = [pytest.bucket_origin, pytest.bucket_processed]

    for bucket in buckets:
        s3.create_bucket(Bucket=bucket)

    def delete_buckets():
        for bucket in buckets:
            objects = s3.list_objects_v2(Bucket=bucket)
            for content in objects.get('Contents'):
                key = content.get('Key')
                s3.delete_object(Bucket=bucket, Key=key)
            else:
                s3.delete_bucket(Bucket=bucket)
    request.addfinalizer(delete_buckets)


@pytest.fixture(scope='function')
def upload_zip_obj(s3):
    bytes_io = BytesIO()
    pytest.key = 'test.zip'
    pytest.file_zipped = 'test.txt'
    pytest.body_zipped = 'test'

    with ZipFile(bytes_io, mode='w') as zip_obj:
        zip_obj.writestr(pytest.file_zipped, pytest.body_zipped)
    bytes_io.seek(0)
    s3.upload_fileobj(bytes_io, pytest.bucket_origin, pytest.key)


@pytest.fixture(scope='session', params=['single', 'multi'])
def event(request):
    with open(f'tests/fixtures/event_{request.param}.json', mode='r') as file_obj:
        return json.load(file_obj)
