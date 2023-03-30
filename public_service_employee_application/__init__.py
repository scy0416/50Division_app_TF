from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

import config

# 데이터베이스 생성
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Flask앱 생성
    app = Flask(__name__)
    app.config.from_object(config)

    # DB
    # 데이터베이스 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # 블루프린트

    # 필터

    return app

# Flask앱 생성(실행)
create_app().run(debug=True)