import os
from flask import Flask, request 
import uuid #고유 식별자(파일이름) 생성

# aws s3 SDK
import boto3
from botocore.client import Config

#파일이름 보안 라이브러리
from werkzeug.utils import secure_filename

app = Flask(__name__)

#aws key 환경 변수 가져오기
app.config['S3_BUCKET_NAME'] = 'high-ball'
app.config['S3_ACCESS_KEY'] = os.environ.get('S3_ACCESS_KEY')
app.config['S3_SECRET_KEY'] = os.environ.get('S3_SECRET_KEY')

#s3 연동
s3 = boto3.client(
    's3',
    aws_access_key_id=app.config['S3_ACCESS_KEY'],
    aws_secret_access_key=app.config['S3_SECRET_KEY'],
    config=Config(signature_version='s3v4')
)

@app.route('/')
def hello_world():
    return 'Hello, World!'

#이미지 업로드
@app.route('/imgupload', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    if file:
        folder = 'img/'  # 업로드할 폴더 이름
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]  # UUID를 사용하여 파일 이름 고유성 보장
        key = os.path.join(folder, unique_filename)  # 경로 생성
        
        s3.upload_fileobj(file, app.config['S3_BUCKET_NAME'], key)
        return 'File uploaded successfully', 200
    
    return 'No file selected', 404

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)