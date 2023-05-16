from flask import Blueprint, request, render_template

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import Post, User, Comment
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('employee_notice', __name__, url_prefix='/employee/notice')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    notice_list = Post.query.outerjoin(
        User,
        Post.user_id == User.id
    ).filter(
        User.role == 'ADMIN'
    ).filter(
        Post.subject.contains(q)
    ).order_by(
        Post.create_date.desc()
    ).paginate(page=page, per_page=10)

    return render_template('employee/notice/notice_list.html',
                           notice_list=notice_list, q=q, page=page)


# 공지사항 상세 페이지
@bp.route('/<int:post_id>', methods=['GET'])
@login_required_employee
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter(
        Comment.post_id == post.id
    ).order_by(
        Comment.create_date.asc()
    ).all()

    return render_template('employee/notice/notice_detail.html',
                           post=post, comments=comments)