from flask import Blueprint, render_template

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import Post, User
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('employee', __name__, url_prefix='/employee')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    notices = Post.query.outerjoin(
        User,
        Post.user_id == User.id
    ).filter(
        User.role == 'ADMIN'
    ).order_by(
        Post.create_date.desc()
    ).paginate(page=1, per_page=5).items

    return render_template('employee/main/main.html', notices=notices)