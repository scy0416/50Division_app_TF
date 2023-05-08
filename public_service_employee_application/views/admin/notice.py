from flask import Blueprint, request, render_template, jsonify
from sqlalchemy import and_, desc

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import Post, User
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('admin_notice', __name__, url_prefix='/admin/notice')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 검색 처리 과정
    notice_list = Post.query.outerjoin(User, Post.user_id == User.id).filter(
        and_(
            User.role == 'ADMIN',
            Post.subject.contains(q)
        )
    ).order_by(desc(Post.create_date))
    notice_list = notice_list.paginate(page=page, per_page=10)

    return render_template('admin/notice/notice_list.html', notice_list=notice_list, q=q, page=page)


# 글 작성 페이지
@bp.route('/write', methods=['GET'])
@login_required_admin
def write():
    return render_template('admin/notice/notice_write.html')


# 이미지 저장 처리
@bp.route('/image', methods=['POST'])
@login_required_admin
def image_proc():
    return jsonify({'random':''})