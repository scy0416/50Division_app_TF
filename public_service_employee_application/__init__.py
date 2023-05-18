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
    from views import main_views, auth_views
    from views.admin import (
    index as admin_index,
    pay_stub_views as admin_pay_stub,
    punch_in_out as admin_punch_in_out,
    medical_checkup as admin_medical_checkup,
    notice as admin_notice,
    personal_record as admin_pr,
    join_request as admin_join_request,
    pr_change_request as admin_pr_change_request,
    vacation_request as admin_vacation_request,
    edu as admin_edu,
    request as admin_request,
    grievance as admin_grievance,
    welfare_point as admin_welfare_point
    )
    from views.employee import (
    index as employee_index,
    pay_stub_views as employee_pay_stub,
    punch_in_out as employee_punch_in_out,
    medical_checkup as employee_medical_checkup,
    grievance as employee_grievance,
    personal_record as employee_personal_record,
    edu as employee_edu,
    vacation as employee_vacation,
    notice as employee_notice,
    welfare_point as employee_welfare_point
    )
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    #
    app.register_blueprint(admin_index.bp)
    app.register_blueprint(admin_pay_stub.bp)
    app.register_blueprint(admin_punch_in_out.bp)
    app.register_blueprint(admin_medical_checkup.bp)
    app.register_blueprint(admin_notice.bp)
    app.register_blueprint(admin_pr.bp)
    app.register_blueprint(admin_join_request.bp)
    app.register_blueprint(admin_pr_change_request.bp)
    app.register_blueprint(admin_vacation_request.bp)
    app.register_blueprint(admin_edu.bp)
    app.register_blueprint(admin_request.bp)
    app.register_blueprint(admin_grievance.bp)
    app.register_blueprint(admin_welfare_point.bp)
    #
    app.register_blueprint(employee_index.bp)
    app.register_blueprint(employee_pay_stub.bp)
    app.register_blueprint(employee_punch_in_out.bp)
    app.register_blueprint(employee_medical_checkup.bp)
    app.register_blueprint(employee_grievance.bp)
    app.register_blueprint(employee_personal_record.bp)
    app.register_blueprint(employee_edu.bp)
    app.register_blueprint(employee_vacation.bp)
    app.register_blueprint(employee_notice.bp)
    app.register_blueprint(employee_welfare_point.bp)

    # 필터
    from filter import formal_datetime, getComments, getUser, formal_birth
    app.jinja_env.filters['datetime'] = formal_datetime
    app.jinja_env.filters['comments'] = getComments
    app.jinja_env.filters['getUser'] = getUser
    app.jinja_env.filters['birth'] = formal_birth

    return app

# Flask앱 생성(실행)
create_app().run(host='0.0.0.0', port=3000, debug=True)
#app = create_app()