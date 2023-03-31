from flask import Blueprint, render_template, request, url_for, flash
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect

from public_service_employee_application import db
from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import User
from public_service_employee_application.forms import AddAdmin

# 블루프린트 객체 생성
bp = Blueprint('admin', __name__, url_prefix='/admin')

# 이 블루프린트의 최초 진입점
@bp.route('/', methods=('GET', ))
# 관리자로 로그인이 되었나 확인하는 부분
@login_required_admin
def index():
    #return render_template('base.html')
    return render_template('user/admin_main.html')

# 인사정보 관리창
@bp.route('/pr/', methods=('GET', ))
@login_required_admin
def pr_information():
    adminForm = AddAdmin()
    page = request.args.get('page', type=int, default=1) # 페이지
    user_list = User.query.filter_by(role='USER')
    user_list = user_list.paginate(page=page, per_page=10)
    return render_template('user/user_list.html', user_list=user_list, adminForm=adminForm)

@bp.route('/append/', methods=('POST', ))
@login_required_admin
def append():
    form = AddAdmin()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(role='ADMIN', userid=form.id.data).first()
        if not user:
            user = User(
                userid=form.id.data,
                name='관리자',
                password=generate_password_hash(form.password1.data),
                role='ADMIN'
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('admin.pr_information', adminForm=AddAdmin()))
        else:
            flash('이미 존재하는 관리자입니다.')
    return redirect(url_for('admin.pr_information', adminForm=form))