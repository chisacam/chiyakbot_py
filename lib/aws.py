import requests
import os
from dotenv import load_dotenv
import boto3
load_dotenv(verbose=True)

comprehend = boto3.client(service_name='comprehend', region_name='ap-northeast-2',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))


def detect_sentiment(text):
    return comprehend.detect_sentiment(Text=text, LanguageCode='ko')