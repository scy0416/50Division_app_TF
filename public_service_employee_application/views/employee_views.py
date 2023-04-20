from flask import Blueprint, render_template, request, g, flash, redirect, url_for

from public_service_employee_application import db
from public_service_employee_application.models import Post, User
from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.forms import writeForm, EmployeeUserDetail

from sqlalchemy import and_

# 블루프린트 객체 생성
bp = Blueprint('employee', __name__, url_prefix='/employee')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=('GET',))
# 직원으로 로그인이 되었나 확인하는 부분
@login_required_employee
def index():
    return render_template('user/employee_main.html')


@bp.route('/notice/', methods=('GET', 'POST'))
@login_required_employee
def notice():
    # 입력 폼 생성
    form = writeForm()

    if request.method == 'POST':
        g.form_error = True
    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 검색 처리 과정
    # 실질적인 검색
    notice_list = db.session.query(Post).join(User).filter(
        and_(User.role == 'USER', Post.subject.contains(q))).order_by(Post.create_date.desc())
    notice_list = notice_list.paginate(page=page, per_page=10)

    # 템플릿 출력
    return render_template('user/notice_list.html', notice_list=notice_list, q=q, page=page, form=form)


@bp.route('/notice/<int:post_id>', methods=('GET',))
@login_required_employee
def notice_detail(post_id):
    post = Post.query.get_or_404(post_id)
    # 템플릿 출력
    return render_template('user/notice_detail.html', post=post)


@bp.route('/pr/detail/<int:user_id>', methods=('GET', 'POST'))
@login_required_employee
def user_detail(user_id):
    employeeuserdetailform = EmployeeUserDetail()
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        g.modifyError = True
    if request.method == 'POST' and employeeuserdetailform.validate_on_submit():
        user.phone_num = employeeuserdetailform.phone_num.data
        user.address = employeeuserdetailform.address.data
        db.session.commit()
        g.modifyError = False

    return render_template('user/user_detail.html', user=user, employeeuserdetailform=employeeuserdetailform)
