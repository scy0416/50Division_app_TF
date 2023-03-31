from flask import Blueprint, render_template, request

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import User

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
    page = request.args.get('page', type=int, default=1) # 페이지
    user_list = User.query.filter_by(role='USER')
    user_list = user_list.paginate(page=page, per_page=10)
    return render_template('user/user_list.html', user_list=user_list)