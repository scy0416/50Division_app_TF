from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_wtf.csrf import CSRFProtect

import config

# 데이터베이스 생성
db = SQLAlchemy()
migrate = Migrate()

csrf = None
app = None

def create_app():
    # Flask앱 생성
    app = Flask(__name__)
    app.config.from_object(config)

    # DB
    # 데이터베이스 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    import models

    csrf = CSRFProtect(app)

    # 블루프린트
    from views import main_views, auth_views, employee_views, admin_views
    from views.admin import (
    pay_stub_views as admin_pay_stub,
    punch_in_out as admin_punch_in_out,
    medical_checkup as admin_medical_checkup,
    notice as admin_notice,
    personal_record as admin_pr,
    join_request as admin_join_request,
    pr_change_request as admin_pr_change_request,
    vacation_request as admin_vacation_request,
    )
    from views.employee import (
    pay_stub_views as employee_pay_stub,
    punch_in_out as employee_punch_in_out,
    medical_checkup as employee_medical_checkup
    )
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(employee_views.bp)
    #
    app.register_blueprint(admin_views.bp)
    app.register_blueprint(admin_pay_stub.bp)
    app.register_blueprint(admin_punch_in_out.bp)
    app.register_blueprint(admin_medical_checkup.bp)
    app.register_blueprint(admin_notice.bp)
    app.register_blueprint(admin_pr.bp)
    app.register_blueprint(admin_join_request.bp)
    app.register_blueprint(admin_pr_change_request.bp)
    app.register_blueprint(admin_vacation_request.bp)
    #
    app.register_blueprint(employee_pay_stub.bp)
    app.register_blueprint(employee_punch_in_out.bp)
    app.register_blueprint(employee_medical_checkup.bp)

    # 필터
    from filter import formal_datetime
    app.jinja_env.filters['datetime'] = formal_datetime

    return app

# Flask앱 생성(실행)
#create_app().run(debug=True)
create_app().run(host='0.0.0.0', port=3000, debug=True)
#app = create_app()