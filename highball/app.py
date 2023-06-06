import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid #고유 식별자(파일이름) 생성

# aws s3 SDK
import boto3
from botocore.client import Config

#파일이름 보안 라이브러리
from werkzeug.utils import secure_filename

#Flask - RDS MySQL 설정
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False #한글 깨짐 해결
CORS(app) # 모든 경로에 대해 CORS 활성화

#aws key 환경 변수 가져오기
app.config['S3_BUCKET_NAME'] = 'high-ball'
app.config['S3_ACCESS_KEY'] = os.environ.get('S3_ACCESS_KEY')
app.config['S3_SECRET_KEY'] = os.environ.get('S3_SECRET_KEY')

# Flask-MySQL 설정
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST') #엔드포인트
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')

mysql = MySQL(app)

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

#S3 이미지 업로드
@app.route('/s3/imgupload', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    if file:
        folder = 'img/'  # 업로드할 폴더 이름
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]  # UUID를 사용하여 파일 이름 고유성 보장
        key = os.path.join(folder, unique_filename)  # 경로 생성
        
        s3.upload_fileobj(file, app.config['S3_BUCKET_NAME'], key)
        return str(unique_filename), 200
    
    return 'No file selected', 404

#rds 연동 테스트
@app.route('/db')
def db_test():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM user')
    user = cur.fetchall()
    cur.close()
    
    return str(user)

#진단 데이터 RDS 업로드
@app.route('/db/upload', methods=['POST'])
def upload_to_db():
    #파라미터 받기
    data = request.data.decode('utf-8')
    data = eval(data)
    
    img_path = data['img_path']
    age = data['나이']
    date = data['수술연월일']
    disease = data['진단명']
    cancerPoint = data['암의 위치']
    cancerN = data['암의 개수']
    cancerLen = data['암의 장경']
    NG = data['NG']
    HG = data['HG']
    ER = data['ER']
    PR = data['PR']
    HG_score_1 = data['HG_score_1']
    HG_score_2 = data['HG_score_2']
    HG_score_3 = data['HG_score_3']
    DCIS_or_LCIS = data['DCIS_or_LCIS_여부']
    DCIS_or_LCIS_type = data['DCIS_or_LCIS_type']
    T_category = data['T_category']
    ER_Allred_score = data['ER_Allred_score']
    PR_Allred_score = data['PR_Allred_score']
    KI_67_LI_percent = data['KI-67_LI_percent']
    HER2 = data['HER2']
    HER2_IHC = data['HER2_IHC']
    HER2_SISH = data['HER2_SISH']
    HER2_SISH_ratio = data['HER2_SISH_ratio']
    BRCA_mutation = data['BRCA_mutation']

    # DB Insert
    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO clinical_info (img_path, `나이`, `수술연월일`, `진단명`, `암의 위치`, `암의 개수`, `암의 장경`, NG, HG, HG_score_1, HG_score_2, HG_score_3, DCIS_or_LCIS_여부, DCIS_or_LCIS_type, T_category, ER, ER_Allred_score, PR, PR_Allred_score, `KI-67_LI_percent`, HER2, HER2_IHC, HER2_SISH, HER2_SISH_ratio, BRCA_mutation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (img_path, age, date, disease, cancerPoint, cancerN, cancerLen, NG, HG, HG_score_1, HG_score_2, HG_score_3, DCIS_or_LCIS, DCIS_or_LCIS_type, T_category, ER, ER_Allred_score, PR, PR_Allred_score, KI_67_LI_percent, HER2, HER2_IHC, HER2_SISH, HER2_SISH_ratio, BRCA_mutation))
        mysql.connection.commit()
        cur.close()
        return 'RDS Insert successfully', 200

    except Exception as e:
        return 'RDS Insert failed: ' + str(e), 500

#======CRUD 게시판========
#전체 글 보기
@app.route('/board')
def board():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM board')
    board = cur.fetchall()
    cur.close()
   
    # 각 항목을 딕셔너리로 변환
    keys = ["id", "title", "writer", "content", "createdAt", "updatedAt", "deletedAt", "category", "img_path"]
    result = [dict(zip(keys, item)) for item in board]
    
    return jsonify(result)

#글 상세 보기
@app.route("/board/<int:post_id>", methods=["GET"])
def get_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM board WHERE id = %s', (post_id,))
    board = cur.fetchall()
    cur.close()
    
    # 딕셔너리로 변환
    keys = ["id", "title", "writer", "content", "createdAt", "updatedAt", "deletedAt", "category", "img_path"]
    result = [dict(zip(keys, item)) for item in board]
    
    if result:
        return jsonify(result[0]), 200
    else:
        return '게시글을 찾을 수 없습니다.', 404

#글 작성
@app.route('/board/add', methods=['POST'])
def add_post():
    #파라미터 받기
    data = request.data.decode('utf-8')
    data = eval(data)
    
    writer = data['writer']
    title = data['title']
    content = data['content']
    category = data['category']
    img_path = data['img_path']
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO posts(writer, title, content, category, img_path) VALUES(%s, %s, %s, %s, %s)", (writer, title, content, category, img_path))
        mysql.connection.commit()
        cur.close()
        return 'new posting successfully', 200

    except Exception as e:
        return 'new posting failed: ' + str(e), 500

#글 수정
@app.route('/board/update/<int:id>', methods=['POST'])
def update_post(id):
    #파라미터 받기
    data = request.data.decode('utf-8')
    data = eval(data)
    
    writer = data['writer']
    title = data['title']
    content = data['content']
    category = data['category']
    img_path = data['img_path']
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE board SET(writer=%s, title=%s, content=%s, category=%s, img_path=%s WHERE id=%s)", (writer, title, content, category, img_path, id))
        mysql.connection.commit()
        cur.close()
        return 'new posting successfully', 200

    except Exception as e:
        return 'new posting failed: ' + str(e), 500



if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)