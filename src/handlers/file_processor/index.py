import boto3

from file_processor import FileProcessor

s3 = boto3.client('s3')


def handler(event, context):
    file_processor = FileProcessor(event, context, s3)
    file_processor.main()
