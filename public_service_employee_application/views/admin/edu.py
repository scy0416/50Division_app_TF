from flask import Blueprint, request, render_template, Response

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import User
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('admin_edu', __name__, url_prefix='/admin/edu')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    page = request.args.get('page', type=int, default=1)
    q = request.args.get('q', type=str, default='')
    print('['+str(q)+']')

    user_list = User.query.filter(User.role == 'USER')
    user_list = user_list.filter(User.name.contains(q))

    user_list = user_list.paginate(page=page, per_page=5)

    return render_template('admin/edu/edu_list.html',
                           user_list=user_list, q=q, page=page)


# 성희롱 예방교육 편집
@bp.route('/SHP/<int:user_id>', methods=['POST'])
@login_required_admin
def SHP(user_id):
    value = request.form.get('value')
    user = User.query.get_or_404(user_id)
    user.sexual_harassment_prevent = value
    db.session.commit()
    return Response(status=204)


# 장애인식 개선교육 편집
@bp.route('/DAI/<int:user_id>', methods=['POST'])
@login_required_admin
def DAI(user_id):
    value = request.form.get('value')
    user = User.query.get_or_404(user_id)
    user.disability_awareness_improvement = value
    db.session.commit()
    return Response(status=204)


# 직장 내 괴롭힘 예방교육 편집
@bp.route('/WHP/<int:user_id>', methods=['POST'])
@login_required_admin
def WHP(user_id):
    value = request.form.get('value')
    user = User.query.get_or_404(user_id)
    user.workplace_harassment_prevent = value
    db.session.commit()
    return Response(status=204)