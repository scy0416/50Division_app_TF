import os

# 데이터베이스접속 주소
SQLALCHEMY_DATABASE_URI ='mysql+pymysql://dev:0000@203.228.27.247/50division tf db'

# SQLAlchemy의 이벤트를 처리하는 옵션
SQLALCHEMY_TRACK_MODIFICATIONS =False

SECRET_KEY = 'dev'