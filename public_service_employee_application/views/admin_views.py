from flask import Blueprint, render_template, request, url_for, flash, g
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
@bp.route('/pr/', methods=('GET', 'POST'))
@login_required_admin
def pr_information():
    adminForm = AddAdmin()

    if 'addAdmin_error' in g:
        del g.addAdmin_error

    if request.method == 'POST':
        g.addAdmin_error = True

    if request.method == 'POST' and adminForm.validate_on_submit():
        user = User.query.filter_by(role='ADMIN', userid=adminForm.id.data).first()
        if not user:
            user = User(
                userid=adminForm.id.data,
                name='관리자',
                password=adminForm.password1.data,
                role='ADMIN'
            )
            db.session.add(user)
            db.session.commit()
            g.addAdmin_error = False
            redirect(url_for('admin.pr_information'))
        else:
            flash('이미 존재하는 관리자입니다.')

    page = request.args.get('page', type=int, default=1) # 페이지
    user_list = User.query.filter_by(role='USER')
    user_list = user_list.paginate(page=page, per_page=10)

    return render_template('user/user_list.html', user_list=user_list, adminForm=adminForm)