import os
from flask import Flask, request 

# aws s3 SDK
import boto3
from botocore.client import Config

#파일이름 보안 라이브러리
from werkzeug.utils import secure_filename

app = Flask(__name__)

#S3 환경 변수 설정
app.config['S3_BUCKET_NAME'] = 'high-ball'
app.config['S3_ACCESS_KEY'] = os.environ.get('S3_ACCESS_KEY')
app.config['S3_SECRET_KEY'] = os.environ.get('S3_SECRET_KEY')

s3 = boto3.client(
    's3',
    aws_access_key_id=app.config['S3_ACCESS_KEY'],
    aws_secret_access_key=app.config['S3_SECRET_KEY'],
    config=Config(signature_version='s3v4')
)

@app.route('/')
def hello_world():
    return 'Hello, World!'

#환경 변수 access key 확인
@app.route('/key')
def key():
    S3_ACCESS_KEY = app.config['S3_ACCESS_KEY']
    S3_SECRET_KEY = app.config['S3_SECRET_KEY']
    print('엑세스',S3_ACCESS_KEY)
    print('시크릿',S3_SECRET_KEY)
    
    return '터미널확인'

#파일 업로드
@app.route('/imgupload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        s3.upload_fileobj(file, app.config['S3_BUCKET_NAME'], filename)
        return 'File uploaded successfully', 200
    
    return 'No file selected', 404