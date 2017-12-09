from io import BytesIO
from zipfile import ZipFile
import os

import maya
import boto3
import pytest


@pytest.fixture(scope='session')
def s3():
    s3 = boto3.client('s3')

    return s3


@pytest.fixture(scope='session')
def buckets(s3):
    buckets = {}
    stack_name = os.getenv('STACK_NAME')
    cfn = boto3.client('cloudformation')

    stack_outputs = cfn.describe_stacks(StackName=stack_name).get('Stacks')[0].get('Outputs')

    for stack_output in stack_outputs:
        for output_value in stack_output.values():
            if output_value == 'BucketOriginName':
                buckets.update({'BucketOriginName': stack_output.get('OutputValue')})
            elif output_value == 'BucketProcessedName':
                buckets.update({'BucketProcessedName': stack_output.get('OutputValue')})
    else:
        return buckets


@pytest.fixture(scope='session')
def s3_prefix():
    now = maya.now()
    now_datetime = now.datetime(to_timezone=now.local_timezone)
    s3_prefix = now_datetime.strftime('%Y/%m/%d')

    return s3_prefix


@pytest.fixture(scope='function')
def upload_zip_obj(s3, s3_prefix, buckets, request):
    bytes_io = BytesIO()
    bucket_origin = buckets.get('BucketOriginName')
    bucket_processed = buckets.get('BucketProcessedName')
    key = 'test.zip'
    pytest.file_zipped = 'test.txt'
    pytest.body_zipped = 'test'

    with ZipFile(bytes_io, mode='w') as zip_obj:
        zip_obj.writestr(pytest.file_zipped, pytest.body_zipped)
    bytes_io.seek(0)
    s3.upload_fileobj(bytes_io, bucket_origin, key)

    def delete_zip_obj():
        for b, k in zip([bucket_origin, bucket_processed], [key, f'{s3_prefix}/{pytest.file_zipped}']):
            s3.delete_object(Bucket=b, Key=k)
    request.addfinalizer(delete_zip_obj)
